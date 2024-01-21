from django.db import models

from .constants import (CHARACTER_QUANTITY,
                        NAME_LENGTH, SLUG_LENGTH)


class BaseModel(models.Model):
    slug = models.SlugField('Слаг', max_length=SLUG_LENGTH,
                            unique=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField('Категория', max_length=NAME_LENGTH,
                            unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class Genre(BaseModel):
    name = models.CharField('Жанр', max_length=NAME_LENGTH,
                            unique=True)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class Title(models.Model):
    name = models.CharField('Произведение',
                            max_length=NAME_LENGTH)
    year = models.PositiveSmallIntegerField('Год')
    description = models.TextField('Текст', blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр',
                                   through='GenreTitle')
    category = models.ForeignKey(Category, verbose_name='Категория',
                                 on_delete=models.SET_NULL,
                                 null=True)
    # rating integer (Рейтинг на основе отзывов, если отзывов нет — `None`)

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return (f'{self.title[:CHARACTER_QUANTITY]}'
                f'-{self.genre[:CHARACTER_QUANTITY]}')
