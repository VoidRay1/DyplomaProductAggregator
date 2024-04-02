import asyncio
import aiohttp
import re
from django.conf import settings
from aggregator.models import Shop, Product, Price, Promotion
from bs4 import BeautifulSoup

def get_products():
    shop = Shop.objects.get(pk=settings.TAVRIA_ID)
    categories = list(shop.categories.filter(available=True, parent__isnull=False).values('id', 'translations__name', 'category_slug'))
    results = asyncio.run(run(shop.api, categories))
    products = [item for sublist in results for item in sublist]
    print(f'🔴  Tavria all products: {len(products)}')
    product_ids = update_data(shop, products)
    Product.objects.filter(shop=shop).exclude(id__in=product_ids).update(available=False)
    result = Product.objects.filter(id__in=product_ids).update(available=True)
    print(f'🔴  Tavria available: {result}')

async def run(url, categories=None):
    tasks = [get_category_products(url, category) for category in categories]
    return await asyncio.gather(*tasks)

async def get_category_products(url, category):
    url += category['category_slug'] + '/catalog'
    params = {'page': 1}
    products, pages = await fetch_page(url, params, category)
    for page in range(2, pages+1):
        params['page'] = page
        next, _ = await fetch_page(url, params.copy(), category)
        products += next
    print(f'🔴  Tavria {category["translations__name"]}: {len(products)}')
    return products

async def fetch_page(url, params, category):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                products = []
                page_content = await response.text()
                soup = BeautifulSoup(page_content, "html.parser")
                pages = parse_pagination(soup.find('ul', class_='pagination'))
                products_list = soup.find('div', class_='catalog-products__container').find_all('div', class_='products__item')
                for product_element in products_list:
                    product_id = product_element.get('id')
                    if product_id:
                        product = parse_product(product_element, category)
                        products.append(product)
                return products, pages
            else:
                return None
        
def parse_product(product_element, category):
    title = product_element.find('p', class_='product__title').find('a').text.strip()
    volume = ''
    match = re.search(r"(?P<volume>\d+,?\d* г|кг)", title)
    if match:
        volume = match.group("volume")
        title = title.replace(match.group("volume"), "")
    title = re.sub(r"\s+", " ", title)
    product = {
        'id': product_element.get('id'),
        'category_id': category['id'],
        'category_slug': category['category_slug'],
        'brand': '',
        'title': title,
        'volume': volume,
        'image_url': product_element.find('div', class_='product__image').find('img').get('src'),
        'price': float(product_element.find('span', class_='price__discount').text.strip().replace('₴', '')),
        'old_price': float(product_element.find('span', class_='price__old').text.strip().replace('₴', '')),
    }
    discount_element = product_element.find('div', class_='product_discount')
    if discount_element:
        product['discount_percentage'] = discount_element.find('span', class_='percentage__info').text.strip()
        product['discount_amount'] = float(discount_element.find('span', class_='money__info').text.strip().replace('₴', ''))
    else:
        product['discount_percentage'] = None
        product['discount_amount'] = 0

    return product

def parse_pagination(data):
    if not data:
        return 1
    for li in data.find_all('li', class_='page-item'):
        link = li.find('a', class_='page-link')
        if link and link.get('aria-label') == 'Next':
            return int(link.get('href').split('=')[-1])
    return 1

def update_data(shop, products = None):
    items_updated = 0
    product_ids = []
    for item in products:
        product, created = Product.objects.get_or_create(
            shop=shop,
            external_id=item['id'],
            defaults={
                'category_id': item['category_id'],
                'name': item['title'],
                'brand': item['brand'],
                'product_slug': item['id'],
                'category_slug': item['category_slug'],
                'image': item['image_url'],
                'volume': item['volume'],
            }
        )
        product_ids.append(product.id)
        discount = item['discount_amount']
        percent = abs(float(item['discount_percentage'].replace('%', '')))
        price = Price.objects.filter(product=product).first() # order by DESC
        if not price or (float(price.price) != float(item['price'])) or (float(price.discount) != float(discount)):
            print(f'🔴  {product}: {float(item["price"])} ({percent}%)')
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
        price.save()
        promotion = Promotion.objects.filter(shop=shop, slug='percent').first()
        price.promotions.add(promotion)
    print(f'🔴  pull: {len(products)} updated: {items_updated}')
    return product_ids