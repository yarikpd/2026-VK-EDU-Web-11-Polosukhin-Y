from datetime import datetime


def get_popular_tags():
    # TODO: Implement DB
    tags = [
        {'id': 'python', 'name': 'Python'},
        {'id': 'django', 'name': 'Django'},
        {'id': 'bootstrap', 'name': 'Bootstrap'},
        {'id': 'html', 'name': 'HTML'},
        {'id': 'css', 'name': 'CSS'},
        {'id': 'javascript', 'name': 'JavaScript'},
        {'id': 'git', 'name': 'Git'},
        {'id': 'linux', 'name': 'Linux'},
        {'id': 'sql', 'name': 'SQL'},
        {'id': 'postgresql', 'name': 'PostgreSQL'}
    ]
    return tags

def get_popular_members():
    # TODO: Implement DB
    members = [
        {'firstname': 'Алексей', 'lastname': 'Иванов', 'questions': 128},
        {'firstname': 'Мария', 'lastname': 'Петрова', 'questions': 115},
        {'firstname': 'Дмитрий', 'lastname': 'Смирнов', 'questions': 98},
        {'firstname': 'Екатерина', 'lastname': 'Кузнецова', 'questions': 87},
        {'firstname': 'Андрей', 'lastname': 'Попов', 'questions': 76},
        {'firstname': 'Ольга', 'lastname': 'Соколова', 'questions': 65},
        {'firstname': 'Сергей', 'lastname': 'Лебедев', 'questions': 54},
        {'firstname': 'Анна', 'lastname': 'Козлова', 'questions': 43},
        {'firstname': 'Иван', 'lastname': 'Новиков', 'questions': 32},
        {'firstname': 'Елена', 'lastname': 'Морозова', 'questions': 21}
    ]
    return members

def get_sidebar_context():
    return {
        'popular_tags': get_popular_tags(),
        'best_members': get_popular_members(),
    }


def get_questions():
    # TODO: Implement DB
    return [
        {
            'id': 1,
            'details': 'В шаблоне использую относительный путь к файлу. Подскажите, какие настройки нужно проверить и для чего нужен тег static?',
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


def get_answers(question_id):
    # TODO: Implement DB
    authors = {question['id']: question['author'] for question in get_questions()}
    answers = {
        1: [
            {
                'id': 1,
                'author': authors[2],
                'text': "Добавьте приложение в INSTALLED_APPS и проверьте STATIC_URL. В начале шаблона подключите {% load static %}, а путь к CSS укажите через {% static 'css/style.css' %}.",
                'rating': 16,
                'vote': 'up',
                'is_accepted': True,
            },
            {
                'id': 2,
                'author': authors[3],
                'text': 'Для общей статики проекта также можно указать STATICFILES_DIRS. Во время разработки файлы отдает runserver при DEBUG=True.',
                'rating': 5,
                'vote': 'none',
                'is_accepted': False,
            },
            {
                'id': 3,
                'author': authors[1],
                'text': 'Проверьте вкладку Network в инструментах разработчика. Код 404 у CSS поможет понять, какой путь запрашивает браузер.',
                'rating': 2,
                'vote': 'none',
                'is_accepted': False,
            },
        ],
        2: [
            {
                'id': 4,
                'author': authors[1],
                'text': 'Добавьте row и две колонки col-12 col-md-6. На телефоне они займут всю ширину, а от 768 px расположатся рядом.',
                'rating': 7,
                'vote': 'none',
                'is_accepted': True,
            },
            {
                'id': 5,
                'author': authors[3],
                'text': 'Поместите сетку в container, а для отступов между колонками используйте g-3 или g-4.',
                'rating': 3,
                'vote': 'none',
                'is_accepted': False,
            },
        ],
    }.get(question_id, [])
    for answer in answers:
        answer['created_at'] = datetime.fromisoformat('2026-10-22T11:00:00+03:00')
    return sorted(answers, key=lambda answer: (-answer['rating'], answer['created_at']))
