from django.contrib import admin
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser
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
        max_length=max(len(ROLES[1]) for ROLES in ROLES),
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
        max_length=USERNAME_LENGTH,
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
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username[:CHARACTER_QUANTITY]


class SlugNameModel(models.Model):
    slug = models.SlugField('Слаг', max_length=SLUG_LENGTH,
                            unique=True)
    name = models.CharField('Название', max_length=NAME_LENGTH,
                            unique=True)

    class Meta:
        abstract = True
        ordering = ('slug',)

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class Category(SlugNameModel):
    pass

    class Meta(SlugNameModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Genre(SlugNameModel):
    pass

    class Meta(SlugNameModel.Meta):
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


class ReviewCommentContent(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации'
    )
    text = models.TextField(verbose_name='текст')

    def __str__(self):
        return (
            f'{self.__class__.__name__}: '
            f'{self.author} - '
            f'"{self.text[:NAME_LENGTH]}" - '
            f'{self.pub_date.strftime("%d.%m.%Y")}'
        )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(ReviewCommentContent):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='название произведения'
    )
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_RATING,
                message=f'Оценка не может быть меньше чем {MIN_RATING}'
            ),
            MaxValueValidator(
                MAX_RATING,
                message=f'Оценка не может быть больше чем {MAX_RATING}'
            )
        ],
        verbose_name='оценка'
    )

    class Meta(ReviewCommentContent.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'title',
                    'author',
                ),
                name='one_author_one_title'
            )
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'


class Comment(ReviewCommentContent):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='комментарий',
        related_name='comments'
    )

    class Meta(ReviewCommentContent.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
