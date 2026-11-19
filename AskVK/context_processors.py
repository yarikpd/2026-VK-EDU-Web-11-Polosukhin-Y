from typing import TypedDict

from django.conf.global_settings import AUTH_USER_MODEL
from django.http.request import HttpRequest

from questions.models import Tag
from questions.services import get_popular_members, get_popular_tags


class SidebarDict(TypedDict):
    popular_tags: list[Tag]
    best_members: list[AUTH_USER_MODEL]

def sidebar(request: HttpRequest) -> SidebarDict:
    return {
        'popular_tags': get_popular_tags(),
        'best_members': get_popular_members(),
    }
