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


class ReviewCommentContent(models.Model):
    author = models.ForeignKey(
        'CustomUser',
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
