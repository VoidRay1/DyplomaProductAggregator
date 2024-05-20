import logging
import telegram
import asyncio
from functools import wraps
from backend.settings import ENABLE_DECORATOR_LOGGING, TELEGRAM_TOKEN
from django.utils import timezone
from telegram_bot.models import UserActionLog, User
from telegram import MessageEntity, Update, InputMediaPhoto
from telegram.ext import ContextTypes

logger = logging.getLogger('default')


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.constants.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def handler_logging(action_name=None):
    """ Turn on this decorator via ENABLE_DECORATOR_LOGGING variable in backend.settings """
    def decor(func):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user, _ = await User.get_user_and_created(update, context)
            action = f"{func.__module__}.{func.__name__}" if not action_name else action_name
            try:
                text = update.message['text'] if update.message else ''
            except AttributeError:
                text = ''
            await UserActionLog.create(user_id=user.user_id, action=action, text=text, created_at=timezone.now())
            return await func(update, context, *args, **kwargs)
        return handler if ENABLE_DECORATOR_LOGGING else func
    return decor


def send_message(user_id, text, parse_mode=None, reply_markup=None, reply_to_message_id=None,
                 disable_web_page_preview=None, entities=None, tg_token=TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        if entities:
            entities = [
                MessageEntity(type=entity['type'],
                              offset=entity['offset'],
                              length=entity['length']
                )
                for entity in entities
            ]

        asyncio.run(bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        ))
    except telegram.error.Forbidden:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success


def send_photo(user_id, photo, caption=None, parse_mode=None, reply_markup=None,
               reply_to_message_id=None, caption_entities=None, tg_token=TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    print(bot)
    try:
        asyncio.run(bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=caption,
            caption_entities=caption_entities,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        ))
    except telegram.error.Forbidden:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success


def send_media_group(user_id, images, caption=None, parse_mode=None, reply_markup=None,
               reply_to_message_id=None, caption_entities=None, tg_token=TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        media_group = []
        for i, img in enumerate(images):
            media_group.append(InputMediaPhoto(open(img, 'rb'), caption = caption if i == 0 else ''))
        asyncio.run(bot.send_media_group(
            chat_id=user_id,
            media = media_group,
            reply_to_message_id=reply_to_message_id,
            # reply_markup=reply_markup,
            # parse_mode=parse_mode,
        ))
    except telegram.error.Forbidden:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success
