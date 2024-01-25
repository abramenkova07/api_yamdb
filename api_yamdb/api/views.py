from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters, generics, mixins, pagination, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import OnlyAdminIfNotGet, IsAdminAuthorModeratorOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer
)
from reviews.models import Category, Genre, Title, Review, CustomUser


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

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related('genre').select_related(
        'category').order_by('id')
    serializer_class = TitleSerializer
    permission_classes = (OnlyAdminIfNotGet,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminAuthorModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminAuthorModeratorOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs['review_id'],
            title=self.kwargs['title_id']
        )
        serializer.save(author=self.request.user, review=review)


class SignUpView(generics.CreateAPIView):
    """Регистрация по username и email."""

    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = CustomUser.objects.get_or_create(
            username=username,
            email=email
        )
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Код подтверждения',
            message=f'Код подтверждения: {confirmation_code}.',
            from_email=settings.EMAIL_ADMIN,
            recipient_list=[user.email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(generics.CreateAPIView):
    """Получение JWT-токена токена."""

    queryset = CustomUser.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(CustomUser, username=username)

        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': f'{token}'},
                status.HTTP_200_OK
            )
        return Response(
            {'message': 'Неверный код.'},
            status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Управление юзерами."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def edit_profile(self, request):
        """Редактирование своего профиля."""

        if request.method == 'PATCH':
            serializer = UserMeSerializer(
                self.request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserMeSerializer(self.request.user)
        return Response(serializer.data)
