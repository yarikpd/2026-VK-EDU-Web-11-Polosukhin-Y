def get_popular_tags():
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