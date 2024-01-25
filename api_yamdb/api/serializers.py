from datetime import datetime
from rest_framework.relations import SlugRelatedField
from rest_framework.exceptions import ValidationError

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, GenreTitle, Title, Comment, Review
from django.db.models import Avg


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


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'

    def create(self, validated_data):
        validated_data._mutable = True
        self.initial_data._mutable = True
        category = self.initial_data['category']
        category = get_object_or_404(Category, slug=category)
        validated_data['category'] = category
        genres = self.initial_data['genre']
        print(self.initial_data)
        print(self.validated_data)
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre = get_object_or_404(Genre, slug=genre)
            GenreTitle.objects.create(genre=current_genre, title=title)
        return title


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    # def create(self, validated_data):
    #     category = self.initial_data['category']
    #     category = get_object_or_404(Category, slug=category)
    #     validated_data['category'] = category
    #     genres = self.initial_data['genre']
    #     title = Title.objects.create(**validated_data)
    #     for genre in genres:
    #         current_genre = get_object_or_404(Genre, slug=genre)
    #         GenreTitle.objects.create(genre=current_genre, title=title)
    #     return title

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
