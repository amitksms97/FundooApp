from django.conf import settings
from rest_framework_jwt import jwt

from user.models import User


class TokenAuthorization:

    """
        Summary:
        --------
        Id will be fetched for the user.
        --------
        Exception:
    """
    @staticmethod
    def token_auth(request):
        key = request.META['HTTP_TOKEN']
        payload = jwt.decode(key, settings.SECRET_KEY, ['HS256'])
        user = User.objects.get(id=payload['id'])
        return user
