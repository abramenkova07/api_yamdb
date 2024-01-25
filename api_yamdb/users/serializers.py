from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import CustomUser
from users.validators import validate_username


class UserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        required=True,
        max_length=50,
        validators=[validate_username,
                    UniqueValidator(queryset=CustomUser.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        max_length=200,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SignUpSerializer(serializers.Serializer):

    username = serializers.CharField(
        required=True,
        max_length=50,
        validators=[validate_username]
    )
    email = serializers.EmailField(
        required=True,
        max_length=200
    )

    # def validate(self, data):

    #     filter_user_email = CustomUser.objects.filter(
    #                       username=data['username'],
    #                       email=data['email']).exists()
    #     filter_user = CustomUser.objects.filter(
    #                       username=data['username']).exists()
    #     filter_email = CustomUser.objects.filter(
    #                       email=data['email']).exists()

    #     if filter_user_email:
    #         return data
    #     if filter_email or filter_user:
    #         raise serializers.ValidationError(
    #             'Такой пользователь уже есть'
    #         )
    #     return data


class TokenSerializer(serializers.Serializer):

    username = serializers.CharField(
        required=True,
        max_length=50,
        validators=[validate_username]
    )
    confirmation_code = serializers.CharField(required=True)


class UserMeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
