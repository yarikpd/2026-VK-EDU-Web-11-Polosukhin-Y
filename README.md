# 2026-VK-EDU-Web-11-Polosukhin-Y

**AskVK** — учебный сайт вопросов и ответов. В этой ветке выполняется ДЗ2: обработка HTTP-запросов, маршрутизация, Django-шаблоны и пагинация на основе верстки из ДЗ1.

## Подготовка переменных окружения

Если `.env.local` или `.env.docker` ещё нет, создайте их из примера:

```sh
cp .env.example .env.local
cp .env.example .env.docker
```

`.env.local` используется при локальном запуске через Django, `.env.docker` — при запуске через Docker Compose.

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

PostgreSQL из Compose доступна на **порту 5430 хоста**.

Если используется собственная PostgreSQL, вставьте её реальные адрес и порт в `.env.local`.

### 3. Запустить сервер

```sh
python manage.py runserver 127.0.0.1:8000
```

Откройте [http://localhost:8000/](http://localhost:8000/).

## Запуск через Docker Compose

Нужен запущенный Docker Engine с Compose и подготовленный `.env.local`.

```sh
docker compose up --build
```

После запуска откройте [http://localhost/](http://localhost/). Порт 80 должен быть свободен.

В Compose три сервиса:

| Сервис | Назначение |
| --- | --- |
| `askvk-postgres` | PostgreSQL; подключение с хоста — `localhost:5430` |
| `askvk_django` | Django через Gunicorn на внутреннем порту 8000 |
| `nginx` | Принимает HTTP-запросы на порту 80, проксирует их в Django и отдаёт `/static/` |

### Автоматический перезапуск при разработке

Чтобы при изменении Python-кода, шаблонов, статики или `scripts/entry.sh` Compose перезапускал Django и повторно выполнял стартовый скрипт, запустите проект с Watch.

```sh
docker compose up --build --watch
```
