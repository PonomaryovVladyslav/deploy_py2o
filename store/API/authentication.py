import base64
import binascii

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.authtoken.models import Token

from config.settings import TOKEN_LIFE_TIME_LIMIT, TOKEN_GENERATE_LINK


class CustomBasicAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_data = get_authorization_header(request).split()

        if not auth_data or auth_data[0].lower() != b'basic':
            return None

        if len(auth_data) == 1:
            message = 'Invalid basic header. No authenticate data.'
            raise exceptions.AuthenticationFailed(message)
        elif len(auth_data) > 2:
            message = 'Invalid basic header. Authenticate data should not contain spaces.'
            raise exceptions.AuthenticationFailed(message)

        try:
            try:
                auth_decoded = base64.b64decode(auth_data[1]).decode('utf-8')
            except UnicodeDecodeError:
                auth_decoded = base64.b64decode(auth_data[1]).decode('latin-1')
            auth_parts = auth_decoded.partition(':')
        except (TypeError, UnicodeDecodeError, binascii.Error):
            message = 'Invalid basic header. Authenticate data not correctly base64 encoded.'
            raise exceptions.AuthenticationFailed(message)

        username, password = auth_parts[0], auth_parts[2]

        user = authenticate(request=request, username=username, password=password)

        if user is None:
            message = 'Invalid username or password.'
            raise exceptions.AuthenticationFailed(message)

        if not user.is_active:
            message = 'User inactive or deleted.'
            raise exceptions.AuthenticationFailed(message)

        return user, None


class CustomTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_data = get_authorization_header(request).split()

        if not auth_data or auth_data[0].lower() != b'token':
            return None

        if len(auth_data) == 1:
            message = 'Invalid token header. No authenticate data.'
            raise exceptions.AuthenticationFailed(message)
        elif len(auth_data) > 2:
            message = 'Invalid token header. Authenticate data should not contain spaces.'
            raise exceptions.AuthenticationFailed(message)

        try:
            key = auth_data[1].decode()
        except UnicodeError:
            message = 'Invalid token header. Token key should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(message)

        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            message = 'Invalid token.'
            raise exceptions.AuthenticationFailed(message)

        user = token.user

        if not user.is_active:
            message = 'User inactive or deleted.'
            raise exceptions.AuthenticationFailed(message)

        token_life_time = (timezone.now() - token.created).seconds

        if token_life_time > TOKEN_LIFE_TIME_LIMIT:
            message = f'The token has expired. Please generate a new token in {TOKEN_GENERATE_LINK}'
            raise exceptions.AuthenticationFailed(message)

        return user, token
