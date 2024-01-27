from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category, Comment, CustomUser, Genre, Review, Title
)
from reviews.validators import validate_username, validate_unique


class AuthorFieldMixin(serializers.Serializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class WriteTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        if value > datetime.today().year:
            raise serializers.ValidationError(
                'Год произведения не может быть позже текущего года.')
        return value


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        if rating:
            return round(rating)
        return None


class ReviewSerializer(AuthorFieldMixin, serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'author', 'text', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST':
            author = request.user
            if Review.objects.filter(title_id=title_id, author=author):
                raise ValidationError('Вы уже оставили отзыв!')
        return data


class CommentSerializer(AuthorFieldMixin, serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment


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

    def validate_role(self, value):
        if value not in ['user', 'admin', 'moderator']:
            raise ValidationError(
                'Нет такой роли.'
            )
        return value


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

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
        )
        validators = (
            validate_unique,
        )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=50,
        validators=[validate_username]
    )
    confirmation_code = serializers.CharField()


class UserMeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)
