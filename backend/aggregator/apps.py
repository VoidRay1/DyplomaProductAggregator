from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AggregatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aggregator'
    verbose_name = _('Shops')