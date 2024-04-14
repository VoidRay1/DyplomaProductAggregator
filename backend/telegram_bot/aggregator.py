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

        url = product.url
        name = product.safe_translation_getter('name', language_code=language_code)
        
        return f'[{name}]({url})\n\n'
    
    def get_random_product():
        random_product = Product.objects.order_by('?').first()
        return (random_product.name, random_product.id, random_product.image)
