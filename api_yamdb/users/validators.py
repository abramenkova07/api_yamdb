import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Логин не может быть "me"'
        )
    if not bool(re.match(r'[\w.@+-]+\Z$', value)):
        raise ValidationError(
            'Некорректные символы в username'
        )
    return value
