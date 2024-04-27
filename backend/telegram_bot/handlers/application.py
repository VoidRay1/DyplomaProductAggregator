"""Telegram event handlers."""

from telegram.ext import (
    Application, filters,
    CommandHandler, MessageHandler,
    InlineQueryHandler, CallbackQueryHandler,
    ChosenInlineResultHandler, PollAnswerHandler,
)

# from celery.decorators import task  # event processing in async mode

from backend.settings import TELEGRAM_TOKEN, TELEGRAM_BOT_USERNAME

from telegram_bot.handlers import admin, commands, files, location
from telegram_bot.handlers.commands import broadcast_command_with_message
from telegram_bot.handlers import handlers as hnd
from telegram_bot.handlers import manage_data as md
from telegram_bot.handlers.static_text import location_command, broadcast_command


def setup_application(app):
    """
    Adding handlers for events from Telegram
    """

    app.add_handler(CommandHandler("start", commands.command_start))

    # admin commands
    app.add_handler(CommandHandler("admin", admin.admin))
    app.add_handler(CommandHandler("stats", admin.stats))

    app.add_handler(MessageHandler(filters.ANIMATION, files.show_file_id))

    # base buttons
    app.add_handler(CallbackQueryHandler(hnd.send_more, pattern=f'^{md.SEND_MORE}'))
    app.add_handler(CallbackQueryHandler(hnd.add_to_fav, pattern=f'^{md.ADD_TO_FAV}'))
    app.add_handler(CallbackQueryHandler(hnd.view_fav, pattern=f'^{md.VIEW_FAV}'))
    app.add_handler(CallbackQueryHandler(hnd.show_products, pattern=f'^{md.PRODUCT_BTN}'))
    app.add_handler(CallbackQueryHandler(hnd.show_product_by_id, pattern=f'^{md.PRODUCT_BY_NAME}'))

    app.add_handler(CallbackQueryHandler(hnd.back_to_main_menu_handler, pattern=f'^{md.BUTTON_BACK_IN_PLACE}'))

    # location
    app.add_handler(CommandHandler(location_command, location.ask_for_location))
    app.add_handler(MessageHandler(filters.LOCATION, location.location_handler))

    app.add_handler(CallbackQueryHandler(hnd.secret_level, pattern=f"^{md.SECRET_LEVEL_BUTTON}"))

    app.add_handler(MessageHandler(filters.Regex(rf'^{broadcast_command} .*'), broadcast_command_with_message))
    app.add_handler(CallbackQueryHandler(hnd.broadcast_decision_handler, pattern=f"^{md.CONFIRM_DECLINE_BROADCAST}"))

    # EXAMPLES FOR HANDLERS
    # app.add_handler(MessageHandler(filters.TEXT, <function_handler>))
    # app.add_handler(MessageHandler(
    #     filters.DOCUMENT, <function_handler>,
    # ))
    # app.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # app.add_handler(MessageHandler(
    #     filters.Chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & filters.FORWARDED & (filters.PHOTO | filters.VIDEO | filters.ANIMATION),
    #     <function_handler>,
    # ))

    return app


def run_pooling():
    """ Run bot in pooling mode """
    bot_link = f"https://t.me/" + TELEGRAM_BOT_USERNAME
    print(f"Pooling of '{bot_link}' started")
    # запускаем приложение 
    app.run_polling(timeout=123)


# @task(ignore_result=True)
async def process_telegram_event(update_json):
    # update = telegram.Update.de_json(update_json, bot)
    # application.process_update(update)
    pass


# Global variable - best way I found to init Telegram bot
app = Application.builder().token(TELEGRAM_TOKEN).build()
app = setup_application(app)
