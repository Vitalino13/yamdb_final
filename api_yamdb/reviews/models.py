from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_year
from user.models import User


class Category(models.Model):
    """Модель, описывающая категории произведений."""
    name = models.CharField(
        verbose_name='Название категории',
        help_text='Введите категорию произведения',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(verbose_name='Slug категории',
                            help_text='Введите Slug категории',
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)


class Genre(models.Model):
    """Модель, описывающая жанры произведений."""
    name = models.CharField(verbose_name='Название жанра',
                            help_text='Введите название жанра',
                            max_length=200)
    slug = models.SlugField(verbose_name='Slug жанра',
                            help_text='Введите Slug жанра',
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=200,
        db_index=True
    )
    year = models.IntegerField(
        'год',
        validators=(validate_year, )
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        'описание',
        max_length=255,
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='жанр',
        through='GenreTitle')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('id',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Review(models.Model):
    """Модель, описывающая отзыв о фильме."""
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        help_text='Оцените фильм от 1 до 10 баллов',
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
        error_messages={'validators': 'Оценка должна быть от 1 до 10!'}
    )
    text = models.TextField(
        verbose_name='Отзыв',
        help_text='Введите ваш отзыв'
    )
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='review_from_author')
        ]


class Comment(models.Model):
    """Модель для оставления комментариев под фильмами."""
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите ваш комментарий'
    )
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comment')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comment')
    pub_date = models.DateTimeField(verbose_name='Дата создания',
                                    auto_now_add=True)

    def __str__(self):
        return self.text
