from datetime import datetime
import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Логин не может быть "me"'
        )
    if not re.match(r'[\w.@+-]+\Z$', value):
        raise ValidationError(
            'Запрещённые символы в никнейме'
        )
    return value


def validate_year(value):
    if value > datetime.today().year:
        raise ValidationError(
            'Год произведения не может быть позже текущего года.')
    return value
