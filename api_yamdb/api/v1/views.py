from api.v1 import permissions, serializers
from api.v1.filters import TitleFilter
from api.v1.utils import send_confirmation_code
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from user.models import User


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'
    permission_classes = (permissions.OnlyAdminCouldSee,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'patch', 'post', 'delete')

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=[IsAuthenticated])
    def user_account_details(self, request):
        """Получение и изменение данных своей учетной записи."""
        if request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup(request):
    """Регистрация нового пользователя."""
    serializer = serializers.UserSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    user, created = User.objects.get_or_create(username=username,
                                               email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_confirmation_code(email, confirmation_code)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_tokens_for_user(request):
    """Получение токена."""
    serializer = serializers.TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    confirmation_code = request.data['confirmation_code']
    if not default_token_generator.check_token(user, confirmation_code):
        return Response({'error': 'Неверный код подтвeрждения!'},
                        status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token)},
                    status=status.HTTP_200_OK)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """Представление категорий произведений."""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (permissions.AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """Представление жанров произведений."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (permissions.AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(ModelViewSet):
    """Представление произведений."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (permissions.AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    """Представление отзывов о фильмах."""
    serializer_class = serializers.ReviewSerializer
    permission_classes = (permissions.AdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        return Review.objects.filter(title__id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return serializer.save(author=self.request.user,
                               title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.AdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        review = Review.objects.get(
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Review,
                                   pk=self.kwargs.get('review_id'),
                                   title__id=self.kwargs.get('title_id'))
        return serializer.save(author=self.request.user, review=review)
