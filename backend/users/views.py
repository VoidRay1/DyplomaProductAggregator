#from django.views.generic import TemplateView
#from django.contrib.auth import logout, get_user_model
#from django.utils.decorators import method_decorator
#from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status, permissions
#from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)        

""""        
class HomeSessionView(TemplateView):
    template_name = 'home_session.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HomeTokenView(TemplateView):
    template_name = 'home_token.html'


class HomeJWTView(TemplateView):
    template_name = 'home_jwt.html'


class HomeKnoxView(TemplateView):
    template_name = 'home_knox.html'


class LogoutSessionView(APIView):

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseDetailView(generics.RetrieveAPIView):
    permission_classes = IsAuthenticated,
    serializer_class = UserSerializer
    model = get_user_model()

    def get_object(self, queryset=None):
        return self.request.user


class UserSessionDetailView(BaseDetailView):
    authentication_classes = (SessionAuthentication, )


class UserTokenDetailView(BaseDetailView):
    authentication_classes = (TokenAuthentication, )


class UserJWTDetailView(SimpleJWTAuthMixin, BaseDetailView):
    pass


class UserKnoxDetailView(KnoxAuthMixin, BaseDetailView):
    pass
"""