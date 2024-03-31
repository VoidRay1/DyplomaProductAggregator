import asyncio
import aiohttp
import re
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion

def get_products():
    shop = Shop.objects.get(pk=settings.ROZETKA_ID)
    categories = list(shop.categories.filter(available=True, parent__isnull=False).values('id', 'translations__name', 'category_slug'))
    results = asyncio.run(run(shop.api, categories))
    products = [item for sublist in results for item in sublist]
    print(f'🟢  Rozetka all products: {len(products)}')
    product_ids = update_data(shop, products)
    Product.objects.filter(shop=shop).exclude(id__in=product_ids).update(available=False)
    result = Product.objects.filter(id__in=product_ids).update(available=True)
    print(f'🟢  Rozetka available: {result}')

async def run(url, categories=None):
    tasks = [get_category_products(url, category) for category in categories]
    return await asyncio.gather(*tasks)

async def get_category_products(url, category):
    params = {
        'category_id': category['category_slug'],
        'page': 1,
    }
    products, pages = await api_request(url, params)
    print(f'🟢  Rozetka {category["translations__name"]} pages: {pages}')
    for page in range(2, pages+1):
        params['page'] = page
        next, _ = await api_request(url, params.copy())
        available = sum(1 for product in next if product['sell_status'] == 'available')
        print(f'🟢  Rozetka {category["translations__name"]} page: {page} available: {available}')
        products += next
        if not available:
            break
    print(f'🟢  Rozetka {category["translations__name"]}: {len(products)}')
    return products

async def api_request(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url + settings.ROZETKA_LIST_PRODUCTS_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                products = await get_products_data(url, data['data']['ids'])
                return products, data['data']['total_pages']
            else:
                return None

async def get_products_data(url, product_ids):
    params = {
        'product_ids': ','.join(str(id) for id in product_ids),
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url + settings.ROZETKA_PRODUCTS_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            else:
                return None
            
def update_data(shop, products = None):
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
    print(f'🟢  Rozetka updated: {items_updated} outStock: {out_stock}')
    return product_ids

def parse_name(title):
    volume = ''
    slug = ''
    match = re.search(r"(?P<slug>\([\w\s\-\/]+\)$)", title)
    if match:
        slug = match.group("slug")[1:-1]
        title = title.replace(match.group("slug"), "")
    match = re.search(r"(?P<volume>[\d\.]+\s*л)", title)
    if match:
        volume = match.group("volume")
        title = title.replace(match.group("volume"), "")
    title = re.sub(r"\s+", " ", title)
    return (title, volume, slug)
