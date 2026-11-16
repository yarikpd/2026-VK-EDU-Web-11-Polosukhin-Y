from typing import TypedDict

from django.http.request import HttpRequest

from questions.services import get_popular_members, get_popular_tags, Tag, PopularMember


class SidebarDict(TypedDict):
    popular_tags: list[Tag]
    best_members: list[PopularMember]

def sidebar(request: HttpRequest) -> SidebarDict:
    return {
        'popular_tags': get_popular_tags(),
        'best_members': get_popular_members(),
    }
