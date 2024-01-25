from datetime import datetime
from rest_framework.relations import SlugRelatedField
from rest_framework.exceptions import ValidationError

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category, Genre, GenreTitle, Title, Comment, Review, CustomUser
)
from reviews.validators import validate_username


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def create(self, validated_data):
        genres = self.initial_data.pop('genre')
        category = self.initial_data.pop('category')
        chosen_category = get_object_or_404(Category, slug=category)
        title = Title.objects.create(**self.initial_data,
                                     category=chosen_category)
        for genre in genres:
            current_genre = get_object_or_404(Genre, slug=genre)
            GenreTitle.objects.create(
                genre=current_genre, title=title)
        return title

    def validate_year(self, value):
        if value > datetime.today().year:
            raise serializers.ValidationError(
                'Год произведения не может быть позже текущего года.')
        return value


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
