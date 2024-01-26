import re

from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.models import CustomUser


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


def validate_unique(data):

    user_email = CustomUser.objects.filter(
        username=data['username'],
        email=data['email']).exists()
    user = CustomUser.objects.filter(
        username=data['username']).exists()
    email = CustomUser.objects.filter(
        email=data['email']).exists()

    if user_email:
        return data
    if email or user:
        raise serializers.ValidationError(
            'Такой пользователь уже зарегистрирован'
        )
    return data
