from celery import shared_task
from aggregator.parse import silpo, rozetka, tavria


@shared_task
def get_silpo_products():
    silpo.get_products()

@shared_task
def get_rozetka_products():
    rozetka.get_products()

@shared_task
def get_tavria_products():
    tavria.get_products()
