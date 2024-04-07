"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import datetime
import telegram
import time
import asyncio
from django.db.models import Q
from django.utils import timezone
from backend.celery import app
from celery.utils.log import get_task_logger

from telegram_bot.handlers import keyboard_utils as kb
from telegram_bot.handlers.utils import send_message, send_photo
from telegram_bot.models import (
    Arcgis,
    User
)
from .aggregator import Aggregator

logger = get_task_logger(__name__)


@app.task(name='send_products', ignore_result=True)
def send_products():
    """Рассылка продуктов пользователям."""

    # Находим пользователей, которым будем слать продукты
    users = User.objects.filter(Q(send_products__isnull=True) |
                                Q(__lte=timezone.now() - datetime.timedelta(hours=24)))
    for user in users:
        aggregator = Aggregator(user)
        product_text, product_id, image = asyncio.run(aggregator.load_products())
        try:
            send_photo(
                user_id=user.user_id,
                photo=open(image, 'rb'),
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
