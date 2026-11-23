# 2026-VK-EDU-Web-11-Polosukhin-Y

**AskVK** — учебный сайт вопросов и ответов на Django и PostgreSQL.

В ДЗ4 добавлены регистрация, вход и выход, редактирование профиля с загрузкой аватара, публикация вопросов с тегами и ответов. Голоса за вопросы и ответы учитываются без перезагрузки страницы. Автор вопроса может отметить правильный ответ.

## Подготовка переменных окружения

Если `.env.local` или `.env.docker` ещё нет, создайте их из примера:

```sh
cp .env.example .env.local
cp .env.example .env.docker
```

`.env.local` используется при локальном запуске через Django, `.env.docker` — при запуске через Docker Compose. Замените заглушки `DJANGO_SECRET`, `POSTGRES_DB`, `POSTGRES_USER` и `POSTGRES_PASSWORD` в обоих файлах.

Новый секретный ключ можно получить командой:

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

## Локальный запуск через Django

Нужны Python 3.14 и доступная PostgreSQL.

### 1. Создать окружение и установить зависимости

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Настроить подключение к PostgreSQL

Можно использовать установленную локально PostgreSQL либо запустить только базу из Compose:

```sh
docker compose up -d --wait askvk-postgres
```

Если используете PostgreSQL из Compose, укажите в `.env.local` `POSTGRES_HOST=127.0.0.1` и `POSTGRES_PORT=5430`. Имя базы, пользователь и пароль должны совпадать с настройками в `.env.docker`.

Если используется собственная PostgreSQL, вставьте её реальные адрес и порт в `.env.local`.

### 3. Загрузить настройки, применить миграции и запустить сервер

```sh
set -a
. ./.env.local
set +a
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Откройте [сайт на порту 8000](http://127.0.0.1:8000/).

## Запуск через Docker Compose

Нужен запущенный Docker Engine с Compose. В `.env.docker` укажите `POSTGRES_HOST=askvk-postgres` и `POSTGRES_PORT=5432`.

```sh
docker compose up --build
```

После запуска откройте [сайт на порту 80](http://localhost/).

В Compose три сервиса:

| Сервис | Назначение |
| --- | --- |
| `askvk-postgres` | PostgreSQL; подключение с хоста — `localhost:5430` |
| `askvk_django` | Django через Gunicorn на внутреннем порту 8000 |
| `nginx` | Принимает HTTP-запросы на порту 80, проксирует их в Django и отдаёт `/static/` и `/media/` |

### Автоматический перезапуск при разработке

Чтобы при изменении Python-кода, шаблонов, статики или `scripts/entry.sh` Compose перезапускал Django и повторно выполнял стартовый скрипт, запустите проект с Watch.

```sh
docker compose up --build --watch
```

## Тестовые данные и админка

Локально выполните команды в окружении с загруженным `.env.local` после применения миграций.

```sh
python manage.py fill_db 2
python manage.py createsuperuser
```

Для запущенного проекта в Docker используйте те же команды внутри контейнера Django.

```sh
docker compose exec askvk_django python manage.py fill_db 2
docker compose exec askvk_django python manage.py createsuperuser
```
