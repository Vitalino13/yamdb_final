from django.contrib.auth.models import AbstractUser
from django.db import models
from reviews.validators import validate_username

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты.',
        max_length=254,
        unique=True,
    )
    bio = models.TextField(
        verbose_name='Биография.',
        blank=True
    )
    role = models.CharField(
        verbose_name='Роль пользователя.',
        max_length=16,
        choices=ROLE_CHOICES,
        default=USER,
    )
    username = models.CharField(
        verbose_name='никнейм',
        max_length=150,
        unique=True,
        validators=(validate_username,),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='12345'
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
