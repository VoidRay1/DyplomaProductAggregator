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
from telegram_bot.models import User
from ..aggregator import Aggregator
from telegram_bot.tasks import broadcast_message
from telegram_bot.utils import convert_2_user_time, extract_user_data_from_update, get_chat_id
from profiles.models import Profile

logger = logging.getLogger('default')


@handler_logging()
async def add_to_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Начинаем процесс добавления в избранное')
    user_id = extract_user_data_from_update(update)['user_id']
    user = await User.get_user(update, context)

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
    user = await User.get_user(update, context)

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
    user = await User.get_user(update, context)
    
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
    user = await User.get_user(update, context)

    query = update.callback_query
    product_name = query.data.split('#')[1]

    aggregator = Aggregator(user)
    product = await aggregator.get_product_by_name(product_name)
    product_text, product_id, image = await aggregator.load_product(id=product.id)

    await context.bot.send_photo(
        chat_id=user_id,
        photo=open(image, 'rb'),
        caption=product_text,
        reply_markup=kb.make_btn_keyboard(),
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )

@handler_logging()
async def back_to_main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):  # callback_data: BUTTON_BACK_IN_PLACE variable from manage_data.py
    user, created = await User.get_user_and_created(update, context)

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
            user_count = await User.count_users(),
            active_24 = await User.active_users()
    )

    await context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=telegram.constants.ParseMode.MARKDOWN
    )


async def broadcast_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): #callback_data: CONFIRM_DECLINE_BROADCAST variable from manage_data.py
    """ Entered /broadcast <some_text>.
        Shows text in Markdown style with two buttons:
        Confirm and Decline
    """
    broadcast_decision = update.callback_query.data[len(md.CONFIRM_DECLINE_BROADCAST):]
    entities_for_celery = await update.callback_query.message.to_dict().get('entities')
    entities = update.callback_query.message.entities
    text = update.callback_query.message.text
    if broadcast_decision == md.CONFIRM_BROADCAST:
        admin_text = st.msg_sent,
        user_ids = list(User.objects.all().values_list('user_id', flat=True))
        broadcast_message.delay(user_ids=user_ids, message=text, entities=entities_for_celery)
    else:
        admin_text = text

    await context.bot.edit_message_text(
        text=admin_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        entities=None if broadcast_decision == md.CONFIRM_BROADCAST else entities
    )