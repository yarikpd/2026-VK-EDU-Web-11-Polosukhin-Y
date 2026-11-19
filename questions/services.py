from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from django.db import models

from .models import Tag


def get_popular_tags() -> list[Tag]:
    return list(Tag.objects.popular()[:10])


def get_popular_members() -> list[AUTH_USER_MODEL]:
    members = list(get_user_model().objects.get_queryset().annotate(
            question_count=models.Count('questions'),
        ).filter(question_count__gt=0).order_by('-question_count', 'id'))[:10]

    return members
