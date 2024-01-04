# from django.core.mail import EmailMessage
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string, get_template
from django.conf import settings

# import threading

# from .serializers import UserSerializer
# import datetime
# from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email

# expire = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]


# def custom_jwt_response_handler(token, user=None, request=None):
#     return {
# 'token': token,
# 'user': UserSerializer(user, context={'request': request}).data,
# 'expire': timezone.now()+expire-datetime.timedelta(seconds=200)
#     }


def validate_email(value: str) -> tuple[bool, str]:
    """Validate a single email."""
    message_invalid = 'Enter a valid email address.'

    if not value:
        return False, message_invalid
    # Check the regex, using the validate_email from django.
    try:
        django_validate_email(value)
    except ValidationError:
        return False, message_invalid

    return True, ''
