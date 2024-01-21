from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, pagination, viewsets

from .permissions import OnlyAdminIfNotGet
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from reviews.models import Category, Genre, Title


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
    permission_classes = (OnlyAdminIfNotGet,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related('genre').select_related(
        'category').order_by('id')
    serializer_class = TitleSerializer
    permission_classes = (OnlyAdminIfNotGet,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
