import os
import csv

from django.core.management.base import BaseCommand
from django.conf import settings
from reviews.models import (Category, Comment, CustomUser,
                            Genre, GenreTitle, Review, Title)

from reviews.models import CustomUser
from django.shortcuts import get_object_or_404


class Command(BaseCommand):

    def uploading_csv(self, file_name, model_name):
        with open(os.path.join(settings.BASE_DIR / f'static/data/{file_name}'),
                  'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            model_name.objects.all().delete()
            for row in reader:
                if 'category' in row:
                    row['category'] = get_object_or_404(
                        Category, id=row['category'])
                if 'author' in row:
                    row['author'] = get_object_or_404(
                        CustomUser, id=row['author'])
                model_name.objects.create(**row)
        self.stdout.write(self.style.SUCCESS(
            f'Данные из "{file_name}" загружены в БД'))

    def handle(self, *args, **options):
        data = {
            'users.csv': CustomUser,
            'category.csv': Category,
            'genre.csv': Genre,
            'titles.csv': Title,
            'genre_title.csv': GenreTitle,
            'review.csv': Review,
            'comments.csv': Comment
        }
        for key, value in data.items():
            self.uploading_csv(key, value)
