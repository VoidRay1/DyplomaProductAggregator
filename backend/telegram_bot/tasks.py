"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import datetime
import telegram
import time
import asyncio
from django.db.models import Q
from django.utils import timezone
from aggregator.models import Product
from aggregator.models import User
from backend.celery import app
from celery.utils.log import get_task_logger

from telegram_bot.handlers import keyboard_utils as kb
from telegram_bot.handlers.utils import send_message, send_photo
from telegram_bot.models import (
    Arcgis,
    User as TelegramUser
)
from .aggregator import Aggregator

logger = get_task_logger(__name__)


@app.task(name='send_products', ignore_result=True)
def send_products():
    """Рассылка продуктов пользователям."""

    # Находим пользователей, которым будем слать продукты
    telegram_users = TelegramUser.objects.filter(Q(send_products__isnull=True)) #|
                                #Q(__lte=timezone.now() - datetime.timedelta(hours=24)))
    users = User.objects.filter(Q(telegram_user__send_products__isnull=True)).select_related('telegram_user')
    for user in users:
        aggregator = Aggregator(user.telegram_user)
        random_product = Product.objects.filter(id__in=user.tracks.filter(active=True).values_list('product', flat=True)).order_by('?').first()
        product_text, product_id, image = (random_product.name, random_product.id, random_product.image) #aggregator.get_random_product() 
        try:
            send_photo(
                user_id=user.telegram_user.telegram_user_id,
                photo=image,
                caption=product_text,
                reply_markup=kb.make_keyboard_for_start_command(product_id),
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
            )
            user.send_products = timezone.now()
            user.save()
        except Exception as e:
            logger.error(f"Failed to send message to {user.user_id}, reason: {e}" )
    return 'ok'


@app.task(ignore_result=True)
def broadcast_message(user_ids, message, entities=None, sleep_between=0.4, parse_mode=None):
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{message}' to {len(user_ids)} users")

    for user_id in user_ids:
        try:
            send_message(user_id=user_id, text=message,  entities=entities, parse_mode=parse_mode)
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}" )
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")


@app.task(ignore_result=True)
def save_data_from_arcgis(latitude, longitude, location_id):
    Arcgis.from_json(Arcgis.reverse_geocode(latitude, longitude), location_id=location_id)
