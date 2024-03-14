from django.urls import path, include
from .views import LogoutAndBlacklistRefreshTokenForUserView

urlpatterns = [
#    path('api/v1/', include('djoser.urls')),
#    path('api/v1/', include('djoser.urls.jwt')),
#    path('api/v1/blacklist/', LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='blacklist'),
#    path('', include('django.contrib.auth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
]