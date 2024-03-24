from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='profile',
                                on_delete=models.CASCADE,
                                verbose_name=_('User'))
#    social_thumb = models.URLField(null=True, blank=True)
    avatar = models.ImageField(upload_to='users/%Y/%m/%d/', null=True, blank=True, verbose_name=_('Avatar'))
    first_name = models.CharField(max_length=500, blank=True, verbose_name=_('First name'))
    last_name = models.CharField(max_length=500, blank=True, verbose_name=_('Last name'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Date of birth'))
    country = models.CharField(max_length=2, blank=True, null=True, verbose_name=_('Country'))
    telegram_username = models.CharField(max_length=500, blank=True, verbose_name=_('Telegram username'))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
