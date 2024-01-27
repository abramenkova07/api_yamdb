from django.contrib import admin

from reviews.models import (Category, Comment,
                            Genre, Review, Title, User)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


class GenreInline(admin.TabularInline):
    model = Title.genre.through
    extra = 0


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'genres', 'category', 'description')
    list_editable = ('category',)
    inlines = (GenreInline,)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'bio',
                    'first_name', 'last_name')
    list_editable = ('role',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
