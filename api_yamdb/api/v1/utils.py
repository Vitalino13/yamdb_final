from django.core.mail import send_mail
from api_yamdb.settings import DEFAULT_FROM_EMAIL


def send_confirmation_code(email, confirmation_code):
    """Отправка кода подтверждения на email."""
    send_mail(
        'Подтверждение регистрации на YaMDB',
        f'Ваш код для завершения регистрации на YaMDB - {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
