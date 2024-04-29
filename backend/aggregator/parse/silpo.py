import asyncio
import aiohttp
import math
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion
from aggregator.signals import product_parser_end_work_signal
import weakref

def get_products():
    shop = Shop.objects.get(pk=settings.SILPO_ID)
    products = asyncio.run(run(shop.api + settings.SILPO_PRODUCTS_URL))
    print(f'🟠  Silpo get products: {len(products)}')
    product_ids = update_data(shop, products)
    Product.objects.filter(shop=shop).exclude(id__in=product_ids).update(available=False)
    result = Product.objects.filter(id__in=product_ids).update(available=True)
    print(f'🟠  Silpo available: {result}')

async def run(url):
    params = {
        'limit': settings.SILPO_MAX_PRODUCTS_LIMIT,
        'offset': 0,
        'deliveryType': 'DeliveryHome',
        'category': settings.SILPO_CATEGORY,
        'includeChildCategories': 'true',
        'sortBy': 'popularity',
        'sortDirection': 'desc',
        'mustHavePromotion': 'false',
    }
    data, pages = await api_request(url, params)
    if pages > 1:
        tasks = []
        for i in range(1, pages):
            params['offset'] += settings.SILPO_MAX_PRODUCTS_LIMIT
            tasks.append(asyncio.create_task(api_request(url, params.copy())))
        results = await asyncio.gather(*tasks)
        data.extend([item for sublist in results for item in sublist])
    return data

async def api_request(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if params['offset'] == 0:
                    pages = math.ceil(data['total'] / params['limit'])
                    print(f'🟠  Silpo total: {data["total"]} pages: {pages}')
                    return data['items'], pages
                else:
                    return data['items']
            else:
                return None

def update_data(shop, products = None):
    products_updated = 0
    out_stock = 0
    updated_products_ids = []
    product_ids = []
    for product in products:
        if product['sectionSlug']:
            category, created = Category.objects.get_or_create(
                shop=shop,
                category_slug=product['sectionSlug'],
                defaults={
                    'name': product['sectionSlug'],
                }
            )
        if not category:
            print(f'❗️  {product}')
        new_product, created = Product.objects.get_or_create(
            shop=shop,
            external_id=product['externalProductId'],
            defaults={
                'category': category,
                'name': product['title'],
                'brand': product['brandTitle'] if product['brandTitle'] else '',
                'product_slug': product['slug'],
                'category_slug': product['sectionSlug'] if product['sectionSlug'] else '',
                'image': settings.SILPO_IMAGES_URL + product['icon'],
                'volume': product['displayRatio'],
            }
        )
        product_ids.append(new_product.id)
        if not new_product.category or (new_product.category != category):
            new_product.category = category
            new_product.save()
        if product['oldPrice'] == None:
            product['oldPrice'] = product['price']
        discount = round(product['oldPrice'] - product['price'], 2)
        percent = round(discount / product['oldPrice'] * 100)
        price = Price.objects.filter(product=new_product).first() # order by DESC
        if not price or (float(price.price) != float(product['price'])) or (float(price.discount) != float(discount)):
            print(f'🟠  {new_product}: {float(product["price"])} ({percent}%)')
            if price:
                print(f'⚖️  old price: {float(price.price)} ({round(price.percent)}%)   {float(price.discount)} = {float(discount)}')
                price.available = False
                price.save()
            price = Price(
                product=new_product,
                price=product['price'],
                currency='UAH',
                discount=discount,
                percent=percent
            )
            updated_products_ids.append(new_product.id)
            products_updated += 1
        # price.percent = round(price.discount / (price.price + price.discount) * 100)
        price.available = product['stock'] > 0
        if not product['stock']:
            out_stock +=1
        price.save()
        if product['promotions']:
            price.promotions.clear()
        for prom in product['promotions']:
            promotion, created = Promotion.objects.get_or_create(
                shop=shop,
                slug=prom['id'],
                defaults={
                    'title': prom['id'],
                    'icon_url': prom['iconPath'],
                }
            )
            price.promotions.add(promotion)
    print(f'🟠  Silpo updated: {products_updated} outStock: {out_stock}')
    product_parser_end_work_signal.send(sender=object, updated_products_ids=updated_products_ids)
    return product_ids