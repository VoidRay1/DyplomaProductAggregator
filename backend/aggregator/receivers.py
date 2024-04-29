from django.dispatch import receiver
from aggregator import signals
from aggregator.models import Shop

shops_count = Shop.objects.count()
parsers_ended = 0

@receiver(signals.product_parser_end_work_signal)
def handle_product_parser_end_work_signal(updated_products_ids, **kwargs):
    global parsers_ended
    parsers_ended += 1
    if parsers_ended == shops_count:
        parsers_ended = 0
