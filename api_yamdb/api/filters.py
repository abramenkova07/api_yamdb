from rest_framework import filters


class GenreCategoryFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        genre_slug = request.query_params.get('genre', None)
        category_slug = request.query_params.get('category', None)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
