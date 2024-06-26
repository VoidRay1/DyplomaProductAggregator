import requests
import datetime
from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from telegram_bot import utils
from asgiref.sync import sync_to_async
from django.conf import settings
from profiles.models import Profile

class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Config(BaseModel):
    """Модель настроек бота."""

    param_name = models.CharField(_('Param name'), max_length=255)
    param_val = models.TextField(_('Param value'), null=True, blank=True)

    def __str__(self):
        return self.param_name

    class Meta:
        ordering = ['param_name']
        verbose_name = _('Param bot')
        verbose_name_plural = _('Params bot')

    @classmethod
    def load_config(cls) -> Dict[str, str]:
        config_params = cls.objects.all()
        result = {}
        for config_param in config_params:
            result[config_param.param_name] = config_param.param_val

        return result


class User(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='telegram_user',
                                on_delete=models.CASCADE,
                                verbose_name=_('User'))
    telegram_user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=8, null=True, blank=True, help_text="Telegram client's lang")
    deep_link = models.CharField(max_length=64, null=True, blank=True)

    is_blocked_bot = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    send_products = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    @sync_to_async
    def get_user_and_created(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ python-telegram-bot's Update, Context --> User instance """
        data = utils.extract_user_data_from_update(update)
        data['telegram_user_id'] = data.get('user_id')
        data['user_id'] = Profile.objects.filter(telegram_username=data["username"]).first().user_id
        u, created = cls.objects.update_or_create(telegram_user_id=data["telegram_user_id"], defaults=data)

        if created:
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    async def get_user(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        u, _ = await cls.get_user_and_created(update, context)
        return u

    @classmethod
    @sync_to_async
    def get_user_by_username_or_user_id(cls, string):
        """ Search user in DB, return User or None if not found """
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    def invited_users(self):  # --> User queryset 
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @classmethod
    @sync_to_async
    def count_users(cls):
        return User.objects.count()

    @classmethod
    @sync_to_async
    def active_users(cls):
        return User.objects.filter(updated_at__gte=now() - datetime.timedelta(hours=24)).count()

    class Meta:
        verbose_name = _('Telegram user')
        verbose_name_plural = _('Telegram users')


class Location(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"

    @sync_to_async
    def create(self, *args, **kwargs):
        return Location.objects.create(**kwargs)

    def save(self, *args, **kwargs):
        super(Location, self).save(*args, **kwargs)
        # Parse location with arcgis
        from .tasks import save_data_from_arcgis
        save_data_from_arcgis.delay(latitude=self.latitude, longitude=self.longitude, location_id=self.pk)


class Arcgis(BaseModel):
    location = models.OneToOneField(Location, on_delete=models.CASCADE, primary_key=True)

    match_addr = models.CharField(max_length=200)
    long_label = models.CharField(max_length=200)
    short_label = models.CharField(max_length=128)

    addr_type = models.CharField(max_length=128)
    location_type = models.CharField(max_length=64)
    place_name = models.CharField(max_length=128)

    add_num = models.CharField(max_length=50)
    address = models.CharField(max_length=128)
    block = models.CharField(max_length=128)
    sector = models.CharField(max_length=128)
    neighborhood = models.CharField(max_length=128)
    district = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    metro_area = models.CharField(max_length=64)
    subregion = models.CharField(max_length=64)
    region = models.CharField(max_length=128)
    territory = models.CharField(max_length=128)
    postal = models.CharField(max_length=128)
    postal_ext = models.CharField(max_length=128)

    country_code = models.CharField(max_length=32)

    lng = models.DecimalField(max_digits=21, decimal_places=18)
    lat = models.DecimalField(max_digits=21, decimal_places=18)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location}, city: {self.city}, country_code: {self.country_code}"

    @classmethod
    def from_json(cls, j, location_id):
        a = j.get("address")
        l = j.get("location")

        if "address" not in j or "location" not in j:
            return

        arcgis_data = {
            "match_addr": a.get("Match_addr"),
            "long_label": a.get("LongLabel"),
            "short_label": a.get("ShortLabel"),
            "addr_type": a.get("Addr_type"),
            "location_type": a.get("Type"),
            "place_name": a.get("PlaceName"),
            "add_num": a.get("AddNum"),
            "address": a.get("Address"),
            "block": a.get("Block"),
            "sector": a.get("Sector"),
            "neighborhood": a.get("Neighborhood"),
            "district": a.get("District"),
            "city": a.get("City"),
            "metro_area": a.get("MetroArea"),
            "subregion": a.get("Subregion"),
            "region": a.get("Region"),
            "territory": a.get("Territory"),
            "postal": a.get("Postal"),
            "postal_ext": a.get("PostalExt"),
            "country_code": a.get("CountryCode"),
            "lng": l.get("x"),
            "lat": l.get("y")
        }

        arc, _ = cls.objects.update_or_create(location_id=location_id, defaults=arcgis_data)
        return

    @staticmethod
    def reverse_geocode(lat, lng):
        r = requests.post(
            "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode",
            params={
                'f': 'json',
                'location': f'{lng}, {lat}',
                'distance': 50000,
                'outSR': '',
            },
            headers={
                'Content-Type': 'application/json',
            }
        )
        return r.json()


class UserActionLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=128)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, made: {self.action}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"

    @sync_to_async
    def create(self, *args, **kwargs):
        return UserActionLog.objects.create(**kwargs)
