from django.dispatch import receiver
from aggregator import signals
from aggregator.models import Shop
from telegram_bot.handlers import handlers

shops_count = Shop.objects.count()
all_shops_updated_products_ids = []
parsers_ended = 0

@receiver(signals.product_parser_end_work_signal)
def handle_product_parser_end_work_signal(updated_products_ids, **kwargs):
    global parsers_ended
    global all_shops_updated_products_ids
    parsers_ended += 1
    all_shops_updated_products_ids += updated_products_ids
    if parsers_ended == shops_count:
        parsers_ended = 0
        handlers.send_bookmarked_products_with_discounts(all_shops_updated_products_ids)
        all_shops_updated_products_ids.clear()
