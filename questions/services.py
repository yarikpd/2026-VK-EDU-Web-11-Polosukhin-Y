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

def get_questions():
    # TODO: Implement DB
    questions = [
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
            'answers_count': 7,
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
        {
            'id': 4,
            'title': 'Как передать переменную в шаблон Django?',
            'text': 'Хочу вывести имя пользователя в шаблоне. Где добавить его в контекст?',
            'author': {
                'firstname': 'Алексей',
                'lastname': 'Крылов',
                'initials': 'АК',
                'avatar_color': '#a7687d',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:35:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'django', 'name': 'Django'},
                {'id': 'python', 'name': 'Python'},
            ],
        },
        {
            'id': 5,
            'title': 'Когда использовать include, а когда extends?',
            'text': 'У меня повторяются шапка и карточки. Как разделить шаблоны?',
            'author': {
                'firstname': 'Мария',
                'lastname': 'Смирнова',
                'initials': 'МС',
                'avatar_color': '#627b6e',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:30:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'django', 'name': 'Django'},
                {'id': 'html', 'name': 'HTML'},
            ],
        },
        {
            'id': 6,
            'title': 'Как расположить карточки по центру с Flexbox?',
            'text': 'Карточки выровнены слева. Какие свойства отвечают за выравнивание по двум осям?',
            'author': {
                'firstname': 'Иван',
                'lastname': 'Петров',
                'initials': 'ИП',
                'avatar_color': '#876b88',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:25:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'css', 'name': 'CSS'},
            ],
        },
        {
            'id': 7,
            'title': 'Как связать label с полем формы?',
            'text': 'Нажимаю на подпись, но курсор не переходит в поле. Как связать эти элементы?',
            'author': {
                'firstname': 'Алексей',
                'lastname': 'Крылов',
                'initials': 'АК',
                'avatar_color': '#a7687d',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:20:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'html', 'name': 'HTML'},
            ],
        },
        {
            'id': 8,
            'title': 'Зачем в форме Django нужен CSRF-токен?',
            'text': 'При отправке формы методом POST получаю 403. Что нужно добавить в шаблон?',
            'author': {
                'firstname': 'Мария',
                'lastname': 'Смирнова',
                'initials': 'МС',
                'avatar_color': '#627b6e',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:15:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'django', 'name': 'Django'},
                {'id': 'html', 'name': 'HTML'},
            ],
        },
        {
            'id': 9,
            'title': 'Как сохранить параметры фильтра при пагинации?',
            'text': 'При переходе на следующую страницу исчезает выбранный тег. Как сохранить его в URL?',
            'author': {
                'firstname': 'Иван',
                'lastname': 'Петров',
                'initials': 'ИП',
                'avatar_color': '#876b88',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:10:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'django', 'name': 'Django'},
                {'id': 'python', 'name': 'Python'},
            ],
        },
        {
            'id': 10,
            'title': 'Как отменить добавление файла в Git?',
            'text': 'Выполнил git add для лишнего файла. Можно убрать его из индекса, сохранив изменения?',
            'author': {
                'firstname': 'Алексей',
                'lastname': 'Крылов',
                'initials': 'АК',
                'avatar_color': '#a7687d',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:05:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'git', 'name': 'Git'},
            ],
        },
        {
            'id': 11,
            'title': 'Чем LEFT JOIN отличается от INNER JOIN?',
            'text': 'Хочу вывести вопросы вместе с ответами и сохранить вопросы, у которых пока нет ответов.',
            'author': {
                'firstname': 'Мария',
                'lastname': 'Смирнова',
                'initials': 'МС',
                'avatar_color': '#627b6e',
            },
            'created_at': datetime.fromisoformat('2026-10-22T08:00:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'sql', 'name': 'SQL'},
                {'id': 'postgresql', 'name': 'PostgreSQL'},
            ],
        },
        {
            'id': 12,
            'title': 'Как открыть модальное окно Bootstrap?',
            'text': 'Есть кнопка и разметка окна. Можно ли связать их через атрибуты HTML?',
            'author': {
                'firstname': 'Иван',
                'lastname': 'Петров',
                'initials': 'ИП',
                'avatar_color': '#876b88',
            },
            'created_at': datetime.fromisoformat('2026-10-22T07:55:00+03:00'),
            'rating': 0,
            'answers_count': 0,
            'vote': 'none',
            'tags': [
                {'id': 'bootstrap', 'name': 'Bootstrap'},
                {'id': 'html', 'name': 'HTML'},
            ],
        },
    ]
    return questions


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
            {
                'id': 6,
                'author': authors[2],
                'text': 'Запустите python manage.py findstatic css/style.css. Команда покажет, видит ли Django файл и из какой папки его берёт.',
                'rating': 4,
                'vote': 'none',
                'is_accepted': False,
            },
            {
                'id': 7,
                'author': authors[3],
                'text': 'Если файл лежит в общей папке static проекта, добавьте её в STATICFILES_DIRS. Для папки static внутри приложения достаточно подключить само приложение.',
                'rating': 3,
                'vote': 'none',
                'is_accepted': False,
            },
            {
                'id': 8,
                'author': authors[2],
                'text': 'При запуске через nginx проверьте, что collectstatic уже выполнен, а nginx читает именно каталог со собранными файлами.',
                'rating': 1,
                'vote': 'none',
                'is_accepted': False,
            },
            {
                'id': 9,
                'author': authors[3],
                'text': 'Если ошибка возникает только на вложенной странице, проверьте href: относительный путь static/css/style.css браузер строит от текущего URL.',
                'rating': 0,
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
