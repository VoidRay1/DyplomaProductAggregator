# import logging
import asyncio
import aiohttp
import re
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion

# logger = logging.getLogger()

def get_products():
    shop = Shop.objects.get(pk=settings.METRO_ID)
    categories = list(
        shop.categories.filter(available=True)
        .values('id', 'translations__name', 'category_slug')
    )
    results = asyncio.run(run(shop.api, categories))
    products = [item for sublist in results for item in sublist]
    print(f'🟡  Metro all products: {len(products)}')
    product_ids = update_data(shop, products)
    Product.objects.filter(shop=shop).exclude(id__in=product_ids).update(available=False)
    result = Product.objects.filter(id__in=product_ids).update(available=True)
    print(f'🟡  Metro available: {result}')

async def run(url, categories=None):
    tasks = [get_category_products(url, category) for category in categories]
    return await asyncio.gather(*tasks)

async def get_category_products(url, category):
    filter = settings.METRO_CATEGORY    
    # filter += category['category_slug']
    params = {
        'language': 'uk-UA',
        'country': 'UA', 
        'query': '*',
        'rows': settings.METRO_MAX_PRODUCTS_LIMIT,
        'page': 1,
        'filter': filter,
    }
    products, pages = await api_request(url, params)
    print(f'🟡  Metro {category["translations__name"]} pages: {pages}')
    for page in range(2, pages+1):
        params['page'] = page
        next, _ = await api_request(url, params.copy())
        print(f'🟡  Metro {category["translations__name"]} page: {page}')
        products += next
    print(f'🟡  Metro {category["translations__name"]}: {len(products)}')
    return products

async def api_request(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url + settings.METRO_LIST_PRODUCTS_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                products = await get_products_data(url, data['resultIds'])
                return products, data['totalPages']
            else:
                return None

async def get_products_data(url, product_ids):
    params = {
        'storeIds': '00012', # Одеса, Аеропортівська. ТЦ №12
        'country': 'UA',
        'locale': 'uk-UA',
        'ids': product_ids,
    }
    headers = {
        'CallTreeId': "C352D2EF-6F5C-4CEA-8DB0-2462A384CC90",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url + settings.METRO_PRODUCTS_URL, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return list(data['result'].values())
            else:
                return None

def update_data(shop, products = None):
    products_updated = 0
    product_ids = []
    promotion = Promotion.objects.filter(shop=shop, slug='promotion').first()
    for product in products:
        for variantNumber, variant in product['variants'].items():
            for bundleNumber, bundle in variant['bundles'].items():
                for storeId, store in bundle['stores'].items():
                    external_id = f'{bundle["bundleId"]["articleNumber"]}/{variantNumber}/{bundleNumber}'
                    category_slug, parent_slug = parse_category(variant['categories'][0])
                    parent = Category.objects.filter(category_slug=parent_slug).first()
                    category, created = Category.objects.get_or_create(
                        shop=shop,
                        category_slug=category_slug,
                        parent=parent,
                        defaults={
                            'name': variant['categoryIds'][0]['id'],
                        }
                    )
                    (title, volume) = parse_name(variant['description'])
                    new_product, created = Product.objects.get_or_create(
                        shop=shop,
                        external_id=external_id,
                        defaults={
                            'category': category,
                            'name': title,
                            'brand': bundle['brandName'],
                            'product_slug': bundle['bundleId']['articleNumber'],
                            'category_slug': variant['categoryIds'][0]['id'],
                            'image': bundle['imageUrlL'],
                            'volume': volume,
                        }
                    )
                    new_product.name = title
                    new_product.volume = volume
                    new_product.save()
                    product_ids.append(new_product.id)
                    new_price = store['sellingPriceInfo']['finalPricesInfo']['articleWithTaxesGross']
                    old_price = store['sellingPriceInfo']['grossStrikeThrough']
                    discount = 0
                    percent  = 0
                    if old_price:
                        discount = round(old_price - new_price, 2)
                        percent  = round(discount / old_price * 100)
                    price = Price.objects.filter(product=new_product).first() # order by DESC
                    if not price or (float(price.price) != float(new_price)) or (float(price.discount) != float(discount)):
                        print(f'🟡  {new_product}: {float(new_price)} ({percent}%)')
                        if price:
                            print(f'⚖️  old price: {float(price.price)} ({round(price.percent)}%)   {float(price.discount)} = {float(discount)}')
                            price.available = False
                            price.save()
                        price = Price(
                            product=new_product,
                            price=new_price,
                            currency=store['sellingPriceInfo']['currency'],
                            discount=discount,
                            percent=percent
                        )
                        products_updated += 1
                    price.save()
                    if store['sellingPriceInfo']['promotionLabels'].get('promotion'):
                        if store['sellingPriceInfo']['promotionLabels']['promotion']['type'] == 'promotion':
                            price.promotions.add(promotion)
    print(f'🟡  pull: {len(products)} updated: {products_updated}')
    return product_ids

def parse_category(categories):
    slug = categories['id']
    levels = categories['levels']
    for level in levels:
        if level['id'] == slug:
            slug = str(level['displayName']).replace(' ', '-').lower()
    parent_slug = None
    if len(levels) > 3:
        parent_slug = str(levels[-2]['displayName']).replace(' ', '-').lower()
    return slug, parent_slug

def parse_name(title):
    volume = ''
    match = re.search(r"(?P<volume>[\d\.,]+\s*(кг|г))", title)
    if match:
        volume = match.group("volume")
        title = title.replace(match.group("volume"), "")
    title = re.sub(r"\s+", " ", title).strip()
    return (title, volume)
