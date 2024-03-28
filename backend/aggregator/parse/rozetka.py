import logging
import requests
import re
from time import sleep
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion

logger = logging.getLogger()

def get_products():
    shop = Shop.objects.get(pk=settings.ROZETKA_ID)
    for category in shop.categories.filter(available=True, parent__isnull=False):
        print(f'🟢  {category}')
        get_category_products(shop, category)
    print(f'🟢  Rozetka end')

def get_category_products(shop, category):
    params = {
        'category_id': category.category_slug,
        'page': 1,
    }
    res = requests.get(shop.api + settings.ROZETKA_LIST_PRODUCTS_URL, params)
    logger.info(res)
    product_ids = []
    if res.status_code == 200:
        data = res.json()['data']
        print(f'🟢  Rozetka total products: {data["ids_count"]}')
        product_ids += update_data(shop, data)
        for page in range(2, data['total_pages']+1):
            params['page'] = page
            res = requests.get(shop.api + settings.ROZETKA_LIST_PRODUCTS_URL, params)
            logger.info(res)
            if res.status_code == 200:
                data = res.json()['data']
                product_ids += update_data(shop, data)
        print(f'🟢  Rozetka {category}: {len(product_ids)}')

def update_data(shop, data = None):
    res = requests.get(shop.api + settings.ROZETKA_PRODUCTS_URL, {'product_ids': ','.join(str(id) for id in data['ids'])})
    logger.info(res)
    products = res.json()['data']
    items_updated = 0
    out_stock = 0
    product_ids = []
    for item in products:
        if item['category_id']:
            category, created = Category.objects.get_or_create(
                shop=shop,
                category_slug=item['category_id'],
                defaults={
                    'name': item['category_id'],
                }
            )
        if not category:
            print(f'❗️  {item}')
            return
        if not item['image_main']:
            item['image_main'] = 'goods-stub-dark-grey-big.svg'
        (name, volume, slug) = parse_name(item['title'])
        product, created = Product.objects.get_or_create(
            shop=shop,
            external_id=item['id'],
            defaults={
                'category': category,
                'name': name if name else item['title'],
                'brand': item['brand'] if item['brand'] else '',
                'product_slug': slug if slug else item['id'],
                'category_slug': item['category_id'] if item['category_id'] else '',
                'image': item['image_main'],
                'volume': volume,
            }
        )
        product_ids.append(product.id)
        if not product.category or (product.category != category):
            product.category = category
            product.save()
        if item['old_price'] == None:
            item['old_price'] = item['price']
        discount = round(item['old_price'] - item['price'], 2)
        percent = round(discount / item['old_price'] * 100) if item['old_price'] else 0
        # if percent < 0:
        #     print(item)
        # print(percent)
        # print(item['price_pcs'])
        price = Price.objects.filter(product=product).first() # order by DESC
        if not price or (float(price.price) != float(item['price'])) or (float(price.discount) != float(discount)):
            print(f'🟢  {product}: {float(item["price"])} ({percent}%)')
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
        price.available = item['sell_status'] == 'available'
        if item['sell_status'] != 'available':
            out_stock +=1
        price.save()
        if item['pictograms']:
            price.promotions.clear()
            for prom in item['pictograms']:
                promotion, created = Promotion.objects.get_or_create(
                    shop=shop,
                    slug=prom['id'],
                    defaults={
                        'title': prom['title'],
                        'icon_url': prom['image_url'],
                    }
                )
                price.promotions.add(promotion)
    print(f'🟢  pull: {len(products)} updated: {items_updated} outStock: {out_stock}')
    return product_ids

def parse_name(title):
    volume = ''
    match = re.search(r'([\w\s\-\(\):№%ёЁЇїІіЄєҐґ\.\'`"]+)\s([\d\.]+\s?(г|g|гр|gr|кг|kg))\s([\w\s№ёЁЇїІіЄєҐґ\+\.\'`"]+)?\s(\([\w\s\-\/]+\))?', title)
    if not match:
        match = re.search(r'([\w\s\-\(\):№%ёЁЇїІіЄєҐґ\.\'`"]+)\s(\([\w\s\-\/]+\))', title)
        if not match:
            print(f'❗️  {title}')
            return (title, volume, '')
        return (title, volume, match.group(2))
    else:
        if match.group(2):
            volume = match.group(2)
    name = match.group(1)
    if match.group(4):
        name += match.group(4)
    slug = match.group(5)
    return (name, volume, slug)