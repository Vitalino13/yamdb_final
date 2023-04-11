import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователей."""
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, attrs):
        email = attrs['email']
        username = attrs['username']
        if User.objects.filter(email=email).exists():
            if User.objects.get(email=email).username != username:
                raise ValidationError('Данный емэйл уже зарегестрирован!')
        if User.objects.filter(username=username).exists():
            if User.objects.get(username=username).email != email:
                raise ValidationError('Данный username уже зарегестрирован!')
        return attrs

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('Нельзя использовать username = me')
        if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$', username) is None:
            raise ValidationError(f'Недопустимые символы <{username}> в нике.')
        return username


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей админом."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_first_name(self, value):
        if len(value) > 150:
            raise ValidationError(
                'Поле first_name должно быть короче 150 символов')
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise ValidationError(
                'Поле last_name должно быть короче 150 символов')
        return value


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для создания токенов."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для создания категорий."""

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для создания жанров."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
