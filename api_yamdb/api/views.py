from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, pagination, viewsets
from rest_framework.pagination import LimitOffsetPagination
from api.permissions import IsAdminAuthorModeratorOrReadOnly
from .filters import TitleFilter


from .permissions import OnlyAdminIfNotGet, IsAdminAuthorModeratorOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    ReadTitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    WriteTitleSerializer
)
from reviews.models import Category, Genre, Title, Review


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all().order_by('slug')
    serializer_class = CategorySerializer
    permission_classes = (OnlyAdminIfNotGet,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all().order_by('slug')
    serializer_class = GenreSerializer
    permission_classes = (OnlyAdminIfNotGet, )
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related('genre').select_related(
        'category').order_by('id')
    permission_classes = (OnlyAdminIfNotGet,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ReadTitleSerializer
        return WriteTitleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_slug = self.request.query_params.get('genre', None)
        category_slug = self.request.query_params.get('category', None)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminAuthorModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminAuthorModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs['review_id'],
            title=self.kwargs['title_id']
        )
        serializer.save(author=self.request.user, review=review)
