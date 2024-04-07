import telegram
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.handlers import static_text as st
from telegram_bot.models import User


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Show help info about all secret admins commands """
    u = await User.get_user(update, context)
    if not u.is_admin:
        return

    return await update.message.reply_text(f'{st.secret_level}\n{st.secret_admin_commands}')
    

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Show help info about all secret admins commands """
    u = await User.get_user(update, context)
    if not u.is_admin:
        return

    text = f"""
*Users*: {await User.count_users()}
*24h active*: {await User.active_users()}
    """
    
    return await update.message.reply_text(
        text, 
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )
    