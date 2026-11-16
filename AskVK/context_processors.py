from questions.services import get_popular_members, get_popular_tags


def sidebar(request):
    return {
        'popular_tags': get_popular_tags(),
        'best_members': get_popular_members(),
    }
