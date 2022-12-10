from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from config.settings import TOKEN_LIFE_TIME_LIMIT


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        token_life_time = (timezone.now() - token.created).seconds
        if token_life_time > TOKEN_LIFE_TIME_LIMIT:
            token.delete()
            token = Token.objects.create(user=user)
            token_life_time = 0
        data = {
            'token': token.key,
            'rest_of_life': f'{TOKEN_LIFE_TIME_LIMIT - token_life_time} seconds'
        }
        return Response(data)
