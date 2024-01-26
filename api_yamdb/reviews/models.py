from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from reviews.constants import (CHARACTER_QUANTITY,
                               NAME_LENGTH, SLUG_LENGTH,
                               MAX_RATING, MIN_RATING,
                               ROLES)


class CustomUser(AbstractUser):

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=256,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLES,
        default='user',
        blank=True
    )
    bio = models.TextField(
        'биография',
        blank=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=256,
        null=True,
        blank=False,
        default='XXXX'
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


class Review(models.Model):
    author = models.ForeignKey(
        CustomUser,
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
        CustomUser,
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
