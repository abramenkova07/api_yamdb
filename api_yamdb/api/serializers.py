from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, GenreTitle, Title


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
    # rating = serializers.SerializerMethodField()

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

    # def get_rating(self, obj):
    #     return 0
