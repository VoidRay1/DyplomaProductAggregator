import logging
import requests
from time import sleep
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion

logger = logging.getLogger()

def get_products():
    shop = Shop.objects.get(pk=settings.SILPO_ID)
    params = {
        'limit': settings.SILPO_MAX_PRODUCTS_LIMIT,
        'offset': 0,
        'deliveryType': 'DeliveryHome',
        'category': settings.SILPO_CATEGORY,
        'includeChildCategories': 'true',
        'sortBy': 'popularity',
        'sortDirection': 'desc',
        'mustHavePromotion': 'true',
    }
    res = requests.get(shop.api + settings.SILPO_PRODUCTS_URL, params)
    logger.info(res)
    product_ids = []
    if res.status_code == 200:
        data = res.json()
        product_ids += update_data(shop, data)
        for i in range(1, round(data['total'] / params['limit'])):
            sleep(5)
            params['offset'] = i * params['limit']
            res = requests.get(shop.api + settings.SILPO_PRODUCTS_URL, params)
            logger.info(res)
            if res.status_code == 200:
                data = res.json()
                product_ids += update_data(shop, data)
        Product.objects.filter(shop=shop).exclude(id__in=product_ids).update(available=False)
        result = Product.objects.filter(id__in=product_ids).update(available=True)
        print(f'🟠  Silpo all: {result}')


def update_data(shop, data = None):
    items_updated = 0
    out_stock = 0
    product_ids = []
    for item in data['items']:
        if item['sectionSlug']:
            category, created = Category.objects.get_or_create(
                shop=shop,
                category_slug=item['sectionSlug'],
                defaults={
                    'name': item['sectionSlug'],
                }
            )
        if not category:
            print(f'❗️  {item}')
        product, created = Product.objects.get_or_create(
            shop=shop,
            external_id=item['externalProductId'],
            defaults={
                'category': category,
                'name': item['title'],
                'brand': item['brandTitle'] if item['brandTitle'] else '',
                'product_slug': item['slug'],
                'category_slug': item['sectionSlug'] if item['sectionSlug'] else '',
                'image': item['icon'],
                'volume': item['displayRatio'],
                # 'alcohol': item[''],
            }
        )
        product_ids.append(product.id)
        if not product.category or (product.category != category):
            product.category = category
            product.save()
        if item['oldPrice'] == None:
            item['oldPrice'] = item['price']
        discount = round(item['oldPrice'] - item['price'], 2)
        percent = round(discount / item['oldPrice'] * 100)
        price = Price.objects.filter(product=product).first() # order by DESC
        if not price or (float(price.price) != float(item['price'])) or (float(price.discount) != float(discount)):
            print(f'🟠  {product}: {float(item["price"])} ({percent}%)')
            if price:
                print(f'⚖️  old price: {float(price.price)} ({round(price.percent)}%)   {float(price.discount)} = {float(discount)}')
                price.available = False
                price.save()
            price = Price(
                product=product,
                price=item['price'],
                currency='UAH',
                discount=discount,
                percent=percent
            )
            items_updated += 1
        # price.percent = round(price.discount / (price.price + price.discount) * 100)
        price.available = item['stock'] > 0
        if not item['stock']:
            out_stock +=1
        price.save()
        if item['promotions']:
            price.promotions.clear()
        for prom in item['promotions']:
            promotion, created = Promotion.objects.get_or_create(
                shop=shop,
                slug=prom['id'],
                defaults={
                    'title': prom['id'],
                    'icon_url': prom['iconPath'],
                }
            )
            price.promotions.add(promotion)
    print(f'🟠  pull: {len(data["items"])} updated: {items_updated} outStock: {out_stock}')
    return product_ids
