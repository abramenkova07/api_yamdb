from django.contrib import admin
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from reviews.constants import (CHARACTER_QUANTITY,
                               EMAIL_LEHGTH, NAME_LENGTH,
                               SLUG_LENGTH, MAX_RATING,
                               MIN_RATING, ROLES, USER,
                               USERNAME_LENGTH)
from reviews.validators import validate_username, validate_year


class User(AbstractUser):

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_username],
    )
    email = models.EmailField(
        max_length=EMAIL_LEHGTH,
        unique=True,
        null=False
    )
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'биография',
        blank=True,
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=True
    )

    def __str__(self):
        return str(self.username)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_user(self):
        return self.role == 'user'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username[:CHARACTER_QUANTITY]


class BaseModel(models.Model):
    slug = models.SlugField('Слаг', max_length=SLUG_LENGTH,
                            unique=True)
    name = models.CharField('Название', max_length=NAME_LENGTH,
                            unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class Category(BaseModel):
    pass

    class Meta:
        ordering = ('slug',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Genre(BaseModel):
    pass

    class Meta:
        ordering = ('slug',)
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'


class Title(models.Model):
    name = models.CharField('Произведение',
                            max_length=NAME_LENGTH)
    year = models.SmallIntegerField('Год', validators=[validate_year])
    description = models.TextField('Текст', blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр',
                                   through='GenreTitle')
    category = models.ForeignKey(Category, verbose_name='Категория',
                                 on_delete=models.SET_NULL,
                                 null=True)

    class Meta:
        ordering = ('year',)
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]

    @admin.display(description='Жанры')
    def genres(self):
        return ', '.join([genre.name for genre in self.genre.all()])

    @property
    def rating(self):
        return self.reviews.values('score').aggregate(rating=Avg('score'))[
            'rating']

    @rating.setter
    def rating(self, value):
        self._rating = value


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL,
                              null=True, verbose_name='Жанр')
    title = models.ForeignKey(Title, on_delete=models.SET_NULL,
                              null=True, verbose_name='Произведение')

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'
        ordering = ('genre',)

    def __str__(self):
        return f'{self.genre}'


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    score = models.IntegerField(
        'Оценка',
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='one_author_one_title'
            )
        ]
        ordering = ('-pub_date',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_comments'
    )
    pub_date = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField()

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
