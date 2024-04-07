import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from telegram_bot.handlers.application import run_pooling

if __name__ == "__main__":
    run_pooling()