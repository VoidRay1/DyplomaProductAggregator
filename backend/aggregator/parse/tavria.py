# import asyncio
import logging
import requests
import re
from django.conf import settings
from aggregator.models import Shop, Category, Product, Price, Promotion
# from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup

logger = logging.getLogger()

def get_products():
    shop = Shop.objects.get(pk=settings.TAVRIA_ID)
    products = []
    for category in shop.categories.filter(available=True):
        print(f'🔴  {category}')
        products += get_category_products(shop, category)
    update_data(shop, products)
    print(f'🔴  Tavria end')

def get_category_products(shop, category):
    url = shop.api + category.category_slug
    params = {'page': 1}
    products, pages = api_request(url, params, category)
    for page in range(2, pages+1):
        params['page'] = page
        prod, p = api_request(url, params, category)
        products += prod
    print(f'🔴  Tavria {category}: {len(products)}')
    return products

def api_request(url, params, category):
    pages = 1
    res = requests.get(url, params)
    logger.info(res)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        pages = parse_pagination(soup.find('ul', class_='pagination'))
        products = []
        products_list = soup.find('div', class_='catalog-products__container').find_all('div', class_='products__item')
        for product_element in products_list:
            product_id = product_element.get('id')
            if product_id:
                product = parse_product(product_element, category)
                products.append(product)
    return products, pages

def parse_product(product_element, category):
    title = product_element.find('p', class_='product__title').find('a').text.strip()
    volume = ''
    match = re.search(r"(?P<volume>\d+,?\d* к?г)", title)
    if match:
        volume = match.group("volume")
        title = title.replace(match.group("volume"), "")
    title = re.sub(r"\s+", " ", title)
    price_element = product_element.find('p', class_='product__price')
    old_price = None
    if price_element.find('span', class_='price__with_discount'):
        price = float(price_element.find('span', class_='price__with_discount').find('span', class_='price__discount').text.strip().replace('₴', ''))
        old_price = float(price_element.find('span', class_='price__with_discount').find('span', class_='price__old').text.strip().replace('₴', ''))
    else:
        price = float(price_element.find('b').text.strip().replace('₴', ''))
    product = {
        'id': product_element.get('id'),
        'category_id': category,
        'category_slug': category.category_slug,
        'brand': '',
        'title': title,
        'volume': volume,
        'image_url': product_element.find('div', class_='product__image').find('img').get('src'),
        'price': price,
        'old_price': old_price if old_price else price,
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
    for item in products:
        product, created = Product.objects.get_or_create(
            shop=shop,
            external_id=item['id'],
            defaults={
                'category': item['category_id'],
                'name': item['title'],
                'brand': item['brand'],
                'product_slug': item['id'],
                'category_slug': item['category_slug'],
                'image': item['image_url'],
                'volume': item['volume'],
            }
        )
        discount = item['discount_amount']
        percent = abs(float(item['discount_percentage'].replace('%', ''))) if item['discount_percentage'] else 0
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
        if percent:
            promotion = Promotion.objects.filter(shop=shop, slug='percent').first()
            price.promotions.add(promotion)
    print(f'🔴  pull: {len(products)} updated: {items_updated}')
