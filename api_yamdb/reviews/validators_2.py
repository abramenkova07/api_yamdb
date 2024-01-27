from rest_framework import serializers

from reviews.models import User


def validate_unique(data):

    user_email = User.objects.filter(
        username=data['username'],
        email=data['email']).exists()
    user = User.objects.filter(
        username=data['username']).exists()
    email = User.objects.filter(
        email=data['email']).exists()

    if user_email:
        return data
    if email or user:
        raise serializers.ValidationError(
            'Такой пользователь уже зарегистрирован'
        )
    return data