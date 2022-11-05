from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class TwoFactorAuthException(APIException):
    status_code = status.HTTP_200_OK
    default_detail = _('Code send to email')
    default_code = 'Code send to email'

