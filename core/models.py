from pathlib import Path
from random import choice
from uuid import uuid4

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


AVATAR_COLORS = ('#70545e', '#a7687d', '#627b6e', '#876b88', '#526e86')


def random_avatar_color() -> str:
    return choice(AVATAR_COLORS)


def avatar_upload_path(instance, filename: str) -> str:
    return f'avatars/{uuid4().hex}{Path(filename).suffix.lower()}'


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='пользователь',
    )
    avatar = models.ImageField(
        'аватар',
        upload_to=avatar_upload_path,
        blank=True,
    )
    avatar_color = models.CharField(
        'цвет аватара',
        max_length=7,
        default=random_avatar_color,
        help_text='Цвет фона для аватара с инициалами.',
        validators=[
            RegexValidator(
                regex=r'\A#[0-9a-fA-F]{6}\Z',
                message='Укажите цвет в формате #RRGGBB.',
            ),
        ],
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self) -> str:
        return self.user.get_username()
