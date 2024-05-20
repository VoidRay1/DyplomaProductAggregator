import datetime
import logging
import telegram

from django.utils import timezone
from django.utils.translation import activate, gettext_lazy as _
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.handlers import commands
from telegram_bot.handlers import static_text as st
from telegram_bot.handlers import manage_data as md
from telegram_bot.handlers import keyboard_utils as kb
from telegram_bot.handlers.utils import handler_logging
from users.models import User
from aggregator.models import Product, Track
from django.db.models import Q
from ..aggregator import Aggregator
from telegram_bot.tasks import broadcast_message
from telegram_bot.utils import convert_2_user_time, extract_user_data_from_update, get_chat_id
from telegram_bot.handlers.utils import send_photo
from telegram_bot.models import (
    User as TelegramUser
)

logger = logging.getLogger('default')

def send_bookmarked_products_with_discounts(products_ids):
    print(products_ids)
    tracks = Track.objects.filter(product_id__in=products_ids, active=True)
    users_ids = tracks.values_list('user_id', flat=True).distinct()
    users = User.objects.filter(id__in=users_ids)
    for user in users:
        aggregator = Aggregator(user.telegram_user)
        products = Product.objects.filter(id__in=user.tracks.filter(product_id__in=products_ids, active=True).values_list('product', flat=True))
        for product in products:
            product_text = aggregator.format_product_with_discount(product)
            product_id, image = (product.id, product.image_url)
            try:
                send_photo(
                    user_id=user.telegram_user.telegram_user_id,
                    photo=image,
                    caption=product_text,
                    reply_markup=kb.make_keyboard_for_start_command(product_id),
                    parse_mode=telegram.constants.ParseMode.MARKDOWN,
                )
            except Exception as e:
                logger.error(f"Failed to send message to {user.user_id}, reason: {e}" )
    return 'ok'

@handler_logging()
async def send_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = extract_user_data_from_update(update)['user_id']
    user = await TelegramUser.get_user(update, context)
    aggregator = Aggregator(user)
    product_text, product_id, image = await aggregator.load_product()
    
    await context.bot.send_photo(
        chat_id=user_id,
        photo=image,
        caption=product_text,
        reply_markup=kb.make_keyboard_for_start_command(product_id),
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )

@handler_logging()
async def add_to_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Начинаем процесс добавления в избранное')
    user_id = extract_user_data_from_update(update)['user_id']
    user = await TelegramUser.get_user(update, context)

    # Извлекаем ID продукта из колбека
    query = update.callback_query
    product_id = query.data.split('#')[1]
    logger.info(f'Добавляем в избранное продукт #{product_id}')

    aggregator = Aggregator(user)
    await aggregator.add_to_fav(product_id)
    msg = st.add_to_fav_success

    await context.bot.edit_message_text(
        text=msg,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_keyboard_for_start_command(product_id),
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )


@handler_logging()
async def view_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = extract_user_data_from_update(update)['user_id']
    user = await TelegramUser.get_user(update, context)

    aggregator = Aggregator(user)
    products_first_chars = await aggregator.get_products(only_first_chars=True)
    
    if update.callback_query.message.text:
        await context.bot.edit_message_text(
            text=st.choose_products,
            chat_id=user_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=kb.make_alphabetical_keyboard(products_first_chars),
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=st.choose_products,
            reply_markup=kb.make_alphabetical_keyboard(products_first_chars),
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
        )

@handler_logging()
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = extract_user_data_from_update(update)['user_id']
    user = await TelegramUser.get_user(update, context)
    
    query = update.callback_query
    selected_char = query.data.split('#')[1]

    aggregator = Aggregator(user)
    products = await aggregator.get_products(only_first_chars=False, first_char=selected_char)

    await context.bot.edit_message_text(
        text=st.choose_product,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_products_keyboard(products),
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )


@handler_logging()
async def show_product_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = extract_user_data_from_update(update)['user_id']
    user = await TelegramUser.get_user(update, context)

    query = update.callback_query
    product_id = int(query.data.split('#')[1])

    aggregator = Aggregator(user)
    product = await aggregator.get_product_by_name(product_id)
    product_text, product_id, image = await aggregator.load_product(id=product.id)

    await context.bot.send_photo(
        chat_id=user_id,
        photo=image,
        caption=product_text,
        reply_markup=kb.make_btn_keyboard(),
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )

@handler_logging()
async def back_to_main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):  # callback_data: BUTTON_BACK_IN_PLACE variable from manage_data.py
    user, created = await TelegramUser.get_user_and_created(update, context)

    payload = context.args[0] if context.args else user.deep_link  # if empty payload, check what was stored in DB
    text = st.welcome

    user_id = extract_user_data_from_update(update)['user_id']
    if update.callback_query.message.text:
        await context.bot.edit_message_text(
            chat_id=user_id,
            text=text,
            message_id=update.callback_query.message.message_id,
            reply_markup=kb.make_keyboard_for_start_command(None),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=kb.make_keyboard_for_start_command(None),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )


@handler_logging()
async def secret_level(update: Update, context: ContextTypes.DEFAULT_TYPE): #callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = "Congratulations! You've opened a secret room👁‍🗨. There is some information for you:\n" \
           "*Users*: {user_count}\n" \
           "*24h active*: {active_24}".format(
            user_count = await TelegramUser.count_users(),
            active_24 = await TelegramUser.active_users()
    )

    await context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=telegram.constants.ParseMode.MARKDOWN
    )


async def broadcast_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): #callback_data: CONFIRM_DECLINE_BROADCAST variable from manage_data.py
    pass