"""Головная логика бота."""

import logging
import requests

# from bs4 import BeautifulSoup
from random import randint
from typing import Iterable, Optional
from django.utils.translation import activate, gettext_lazy as _
from telegram_bot.handlers import static_text as st
from telegram_bot.models import User
from users.models import User as SysUser
from profiles.models import Profile
from aggregator.models import Product, Track
from parler.models import TranslatableModel
from django.db.models import Max
from asgiref.sync import sync_to_async

logger = logging.getLogger('default')


class Aggregator:
    def __init__(self, user: User):
        self.user = user
        activate(self.user.language_code)

    @sync_to_async
    def get_products(self, only_first_chars: bool = False, **kwargs):
        """Возврщает список продуктов из избранного пользователя.

        Если передан флаг only_first_chars, то вернут только первые буквы в названии продукта.
        """

        profile = Profile.objects.filter(telegram_username=self.user.username).first()
        products = Track.objects.filter(user=profile.user, active=True)

        if only_first_chars:
            result = set()
            for product in products:
                result.add(product.product.name[0])
        else:
            filter_by_first_char = kwargs.get('first_char')
            return {product.product.id: product.product.name for product in products if product.product.name[0] == filter_by_first_char}

        result = list(result)
        result.sort()
        return result

    @sync_to_async
    def get_product_by_name(self, product_id: int) -> Product:
        queryset = Product.objects.get(id=product_id)
        return queryset

    @sync_to_async
    def add_to_fav(self, id: int) -> None:
        """Добавляет продукт в избранное."""
        product = Product.objects.get(pk=id)
        profile = Profile.objects.filter(telegram_username=self.user.username).first()
        track, created = Track.objects.get_or_create(user=profile.user, product=product)
        track.active = True
        track.save()

    @staticmethod
    def format_product(product: Product, with_description: bool = False, language_code: str = 'uk') -> str:
        """Возвращает продукт в Markdown-ready состоянии."""

        name = product.safe_translation_getter('name', language_code=language_code)
        if not product.volume: 
            volume = ' не вказана на сайті'
        else:
            volume = f': {product.volume}'
        
        return f'Продукт: {name} \nВага{volume} \nЦіна: {product.last_price()} грн\nПосилання на продукт: {product.url}'
    
    def get_random_product():
        random_product = Product.objects.order_by('?').first()
        return (random_product.name, random_product.id, random_product.image)

    @sync_to_async
    def load_product(self, id: int = None) -> (str, Optional[int], Optional[str]):
        """Загружает продукт.

        Если передан id, то продукт выбирается из базы, иначе - загружается случайный с сайта.
        """
        try:
            if id:
                product = Product.objects.get(pk=id)
                with_description = False
            else:
                max_id = Product.objects.filter(available=True).aggregate(max_id=Max("id"))['max_id']
                product = Product.objects.get(pk=randint(1, max_id))
                with_description = True
            image = f'{product.image_url}'
            result = self.format_product(product, with_description, self.user.language_code)
        except Exception as ex:
            logger.error(f'Ошибка в процессе загрузки продукта: {ex}')
            result = f'{st.error}\n{ex}'

        return result, product.id, image