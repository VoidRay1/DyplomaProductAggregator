import datetime
import logging
import re
import telegram

from telegram import Update
from telegram.ext import ContextTypes
from django.utils import timezone
from telegram_bot.handlers import static_text
from telegram_bot.models import User
from telegram_bot.utils import extract_user_data_from_update
from telegram_bot.handlers import static_text as st
from telegram_bot.handlers.keyboard_utils import make_keyboard_for_start_command, keyboard_confirm_decline_broadcasting
from telegram_bot.handlers.utils import handler_logging

logger = logging.getLogger('default')
logger.info("Command handlers check!")


# @handler_logging()
async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, created = await User.get_user_and_created(update, context)

    payload = context.args[0] if context.args else user.deep_link  # if empty payload, check what was stored in DB
    text = f'{st.welcome}\n\n'

    user_id = extract_user_data_from_update(update)['user_id']
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=make_keyboard_for_start_command(None),
        parse_mode=telegram.constants.ParseMode.MARKDOWN
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Show help info about all secret admins commands """
    u = await User.get_user(update, context)
    if not u.is_admin:
        return

    text = f"""
*Users*: {await User.count_users()}
*24h active*: { await User.active_users()}
    """

    return await update.message.reply_text(
        text, 
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def broadcast_command_with_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Type /broadcast <some_text>. Then check your message in Markdown format and broadcast to users."""
    u = User.get_user(update, context)
    user_id = extract_user_data_from_update(update)['user_id']

    if not u.is_admin:
        text = static_text.broadcast_no_access
        markup = None

    else:
        text = f"{update.message.text.replace(f'{static_text.broadcast_command} ', '')}"
        markup = keyboard_confirm_decline_broadcasting()

    try:
        await context.bot.send_message(
            text=text,
            chat_id=user_id,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            reply_markup=markup
        )
    except telegram.error.BadRequest as e:
        place_where_mistake_begins = re.findall(r"offset (\d{1,})$", str(e))
        text_error = static_text.error_with_markdown
        if len(place_where_mistake_begins):
            text_error += f"{static_text.specify_word_with_error}'{text[int(place_where_mistake_begins[0]):].split(' ')[0]}'"
        await context.bot.send_message(
            text=text_error,
            chat_id=user_id
        )