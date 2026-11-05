from datetime import datetime

from django.http import Http404
from django.views.generic import TemplateView

from questions.mixins import SidebarContextMixin


class IndexView(SidebarContextMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO: Implement DB
        questions_list = [
            {
                'id': 1,
                'title': 'Как подключить статические файлы в Django?',
                'text': (
                    'Создал приложение и добавил CSS, но стили не появляются на странице. '
                    'Где нужно хранить статику и как правильно подключить её в шаблоне?'
                ),
                'author': {
                    'firstname': 'Алексей',
                    'lastname': 'Крылов',
                    'initials': 'АК',
                    'avatar_color': '#a7687d',
                },
                'created_at': datetime.fromisoformat('2026-10-22T10:30:00+03:00'),
                'rating': 12,
                'answers_count': 3,
                'vote': 'up',
                'tags': [
                    {'id': 'python', 'name': 'Python'},
                    {'id': 'django', 'name': 'Django'},
                ],
            },
            {
                'id': 2,
                'title': 'Как работает сетка Bootstrap?',
                'text': (
                    'Хочу сделать две колонки на большом экране и одну на телефоне. '
                    'Как правильно использовать container, row и col?'
                ),
                'author': {
                    'firstname': 'Мария',
                    'lastname': 'Смирнова',
                    'initials': 'МС',
                    'avatar_color': '#627b6e',
                },
                'created_at': datetime.fromisoformat('2026-10-22T09:15:00+03:00'),
                'rating': 8,
                'answers_count': 2,
                'vote': 'none',
                'tags': [
                    {'id': 'bootstrap', 'name': 'bootstrap'},
                    {'id': 'css', 'name': 'css'},
                ],
            },
            {
                'id': 3,
                'title': 'Чем отличается GET от POST?',
                'text': (
                    'Разбираюсь с HTML-формами. В каких случаях использовать каждый '
                    'из методов и как передать данные на сервер?'
                ),
                'author': {
                    'firstname': 'Иван',
                    'lastname': 'Петров',
                    'initials': 'ИП',
                    'avatar_color': '#876b88',
                },
                'created_at': datetime.fromisoformat('2026-10-22T08:40:00+03:00'),
                'rating': -1,
                'answers_count': 0,
                'vote': 'down',
                'tags': [
                    {'id': 'http', 'name': 'http'},
                    {'id': 'html', 'name': 'html'},
                ],
            },
        ]

        context['questions'] = questions_list

        # TODO: Implement DB
        questions_pages = 3

        try:
            current_page = int(self.request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise Http404('Некорректный номер страницы')

        if current_page < 1 or current_page > questions_pages:
            raise Http404('Страница не найдена')


        query_params = self.request.GET.copy()
        page_path = self.request.get_full_path().split('?', 1)[0]
        pages_list = []
        for page_number in range(1, questions_pages + 1):
            query_params['page'] = str(page_number)
            pages_list.append({
                'number': page_number,
                'url': f'{page_path}?{query_params.urlencode()}',
            })

        query_params['page'] = str(current_page - 1)
        previous_page_url = f'{page_path}?{query_params.urlencode()}' if current_page > 1 else None
        query_params['page'] = str(current_page + 1)
        next_page_url = f'{page_path}?{query_params.urlencode()}' if current_page < questions_pages else None
        context['pagination'] = {
            'pages_list': pages_list,
            'current_page': current_page,
            'has_previous': current_page > 1,
            'previous_page_url': previous_page_url,
            'has_next': current_page < questions_pages,
            'next_page_url': next_page_url,
        }

        return context
