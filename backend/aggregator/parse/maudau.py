# import logging
import asyncio
import aiohttp
import re
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion

# logger = logging.getLogger()

def get_products():
    shop = Shop.objects.get(pk=settings.MAUDAU_ID)
    categories = list(
        shop.categories.filter(available=True)
        .exclude(children__isnull=False)
        .values('id', 'translations__name', 'category_slug')
    )
    results = asyncio.run(run(shop.api, categories))
    products = [item for sublist in results for item in sublist]
    print(f'🟣  Maudau all products: {len(products)}')
    product_ids = update_data(shop, products)
    Product.objects.filter(shop=shop).exclude(id__in=product_ids).update(available=False)
    result = Product.objects.filter(id__in=product_ids).update(available=True)
    print(f'🟣  Maudau available: {result}')

async def run(url, categories=None):
    tasks = [get_category_products(url, category) for category in categories]
    return await asyncio.gather(*tasks)

async def get_category_products(url, category):
    params = {
        'sort': 'popularity', 
        'offset': 0,
        'limit': settings.MAUDAU_MAX_PRODUCTS_LIMIT,
        'filter[categories][]': category['category_slug'],
    }
    print(f'🟣  Maudau {category["translations__name"]}')
    all_products = []
    while True:
        products = await api_request(url, params)
        if products:
            params['offset'] += settings.MAUDAU_MAX_PRODUCTS_LIMIT
            all_products += products
        else:
            break
    print(f'🟣  Maudau {category["translations__name"]}: {len(all_products)}')
    return all_products

async def api_request(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url + settings.MAUDAU_PRODUCTS_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data['items']
            else:
                return None

def update_data(shop, products = None):
    products_updated = 0
    product_ids = []
    # promotion = Promotion.objects.filter(shop=shop, slug='percent').first()
    for product in products:
        category, created = Category.objects.get_or_create(
            shop=shop,
            category_slug=product['mainCategorySlug'],
            defaults={
                'name': product['mainCategorySlug'],
            }
        )
        (title, volume) = parse_name(product['title'])
        new_product, created = Product.objects.get_or_create(
            shop=shop,
            external_id=product['externalId'],
            defaults={
                'category': category,
                'name': title,
                'brand': product['brandSlug'] if product['brandSlug'] else '',
                'product_slug': product['slug'],
                'category_slug': product['mainCategorySlug'],
                'image': product['mainMedia'],
                'volume': volume,
            }
        )
        product_ids.append(new_product.id)
        offer = product['offers'][0]
        price = Price.objects.filter(product=new_product).first() # order by DESC
        if not price or (float(price.price) != float(offer['price'])) or (float(price.discount) != float(offer['discountValue'])):
            print(f'🟣  {new_product}: {float(offer["price"])} ({offer["discountPercent"]}%)')
            if price:
                print(f'⚖️  old price: {float(price.price)} ({round(price.percent)}%)   {float(price.discount)} = {float(offer["discountValue"])}')
                price.available = False
                price.save()
            price = Price(
                product=new_product,
                price=offer['price'],
                currency='UAH',
                discount=offer['discountValue'],
                percent=offer['discountPercent'],
                available=offer['isAvailable'],
            )
            products_updated += 1
        price.save()
        # if offer['discountValue'] > 0:
        #     price.promotions.add(promotion)
    print(f'🟣  Maudau pull: {len(products)} updated: {products_updated}')
    return product_ids

def parse_name(title):
    volume = ''
    match = re.search(r"(?P<slug>\([\w\s\-\/]+\)$)", title)
    if match:
        # slug = match.group("slug")[1:-1]
        title = title.replace(match.group("slug"), "")
    match = re.search(r"(?P<volume>[\d\.,]+\s*кг?г)", title)
    if match:
        volume = match.group("volume")
        title = title.replace(match.group("volume"), "")
    title = re.sub(r"\s+", " ", title).strip()
    return (title, volume)
