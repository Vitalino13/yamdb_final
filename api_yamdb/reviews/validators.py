import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f'{value} не может быть больше {now}'
        )


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя не может быть <me>.')
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$', value) is None:
        raise ValidationError(f'Недопустимые символы <{value}> в нике.')
    return value
