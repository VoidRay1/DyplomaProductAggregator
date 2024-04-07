import telegram
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.handlers.static_text import share_location, thanks_for_location
from telegram_bot.models import User, Location


async def ask_for_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Entered /ask_location command"""
    u = await User.get_user(update, context)

    await context.bot.send_message(
        chat_id=u.user_id,
        text=share_location,
        reply_markup=telegram.ReplyKeyboardMarkup([
            [telegram.KeyboardButton(text="Send 🌏🌎🌍", request_location=True)]
        ], resize_keyboard=True), #'False' will make this button appear on half screen (become very large). Likely,
        # it will increase click conversion but may decrease UX quality.
    )


async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = await User.get_user(update, context)
    lat, lon = update.message.location.latitude, update.message.location.longitude
    await Location.create(user=u, latitude=lat, longitude=lon)

    await update.message.reply_text(
        thanks_for_location,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )    
