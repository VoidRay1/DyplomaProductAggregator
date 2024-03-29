from django.dispatch import receiver
from djoser.signals import user_registered

from profiles.models import Profile


@receiver(user_registered, dispatch_uid='create_profile')
def create_profile(sender, user, request, **kwargs):
    """Создаём профиль пользователя при регистрации"""
    data = request.data

    Profile.objects.create(
        user=user,
 #       avatar=data.get('avatar', ''),
 #       social_thumb=data.get('social_thumb', '')
    )