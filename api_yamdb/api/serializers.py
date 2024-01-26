from datetime import datetime

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from reviews.models import (
    Category, Genre, Title, Comment, Review, CustomUser
)
from reviews.validators import validate_username


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


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if title.reviews.select_related('title').filter(author=author):
                raise ValidationError('Вы уже оставили отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text'
    )

    class Meta:
        fields = '__all__'
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

    def validate(self, data):

        filter_user_email = CustomUser.objects.filter(
                          username=data['username'],
                          email=data['email']).exists()
        filter_user = CustomUser.objects.filter(
                          username=data['username']).exists()
        filter_email = CustomUser.objects.filter(
                          email=data['email']).exists()

        if filter_user_email:
            return data
        if filter_email or filter_user:
            raise serializers.ValidationError(
                'Такой пользователь уже есть'
            )
        return data


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