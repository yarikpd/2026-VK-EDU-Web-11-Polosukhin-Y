# 2026-VK-EDU-Web-11-Polosukhin-Y

**AskVK** — учебный сайт вопросов и ответов. В этой ветке выполняется ДЗ2: обработка HTTP-запросов, маршрутизация, Django-шаблоны и пагинация на основе верстки из ДЗ1.

Проект использует Python 3.14, Django 6.1, PostgreSQL, Gunicorn и nginx. Python-зависимости указаны в `requirements.txt`. Оформление — Bootstrap 5.3.8 с локальными CSS и JS, тёмной палитрой и адаптивным меню. Кастомного JavaScript нет.

## Подготовка переменных окружения

Все команды ниже выполняются из корня репозитория, если не указано другое.

Если `.env` ещё нет, создайте его из примера:

```sh
cp .env.example .env
```

Существующий `.env` перезаписывать не нужно. Замените заглушки своими значениями. Пример структуры:

```dotenv
DJANGO_SECRET='replace-with-your-generated-secret'
DJANGO_DEBUG=True
POSTGRES_DB=postgres_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD='replace-with-your-password'
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Новый секретный ключ можно получить командой:

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

`.env` не хранится в Git; в репозитории остаётся `.env.example` без секретов. Значения с пробелами или специальными символами, в частности секретный ключ и пароль, заключайте в одинарные кавычки: файл используется и Compose, и оболочкой при локальном запуске. `DJANGO_DEBUG` включает отладку только при точном значении `True`.

## Локальный запуск через Django

Нужны Python 3.14 и доступная PostgreSQL с созданной базой и пользователем из `.env`. Для установки `psycopg2` из исходников также нужны компилятор, клиентские библиотеки PostgreSQL и доступная команда `pg_config`.

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

У текущего Compose база опубликована на **порту 5430 хоста**, а внутри Docker слушает 5432. Healthcheck базы использует имена `postgres_user` и `postgres_db`: если меняете эти значения в `.env`, обновите также команду проверки в `docker-compose.yaml`.

Загрузите переменные в текущую оболочку. `settings.py` читает их через `os.getenv`, автоматической загрузки `.env` в локальном режиме нет:

```sh
set -a
. ./.env
set +a
```

Если используется база из Compose, после загрузки `.env` переопределите адрес и порт для запуска Django на хосте:

```sh
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5430
```

Если используется собственная PostgreSQL, оставьте её реальные адрес и порт из `.env` (обычно `localhost:5432`).

### 3. Выполнить миграции и запустить сервер

```sh
export DJANGO_DEBUG=True
python manage.py collectstatic
python manage.py runserver 127.0.0.1:8000
```

Откройте [http://localhost:8000/](http://localhost:8000/). Остановка — `Ctrl+C`.

Для последующих запусков активируйте `.venv`, загрузите переменные и выполните `runserver`. Переопределения через `export` действуют только в текущей оболочке.

## Запуск через Docker Compose

Нужны запущенный Docker Desktop либо Docker Engine с Compose и подготовленный `.env`. Локальное Python-окружение в этом режиме не требуется.

```sh
docker compose up --build
```

После запуска откройте [http://localhost/](http://localhost/). Порт 80 должен быть свободен. Для запуска в фоне:

```sh
docker compose up --build -d
```

В Compose три сервиса:

| Сервис | Назначение |
| --- | --- |
| `askvk-postgres` | PostgreSQL; подключение с хоста — `localhost:5430` |
| `askvk_django` | Django через Gunicorn на внутреннем порту 8000 |
| `nginx` | Принимает HTTP-запросы на порту 80, проксирует их в Django и отдаёт `/static/` |

Compose переопределяет для Django `POSTGRES_HOST=askvk-postgres`, `POSTGRES_PORT=5432` и `DJANGO_DEBUG=False`. Поэтому локальные параметры подключения из `.env` не мешают работе контейнеров.

При старте `scripts/entry.sh` выполняет `compilemessages`, `makemigrations`, `migrate` и `collectstatic`, затем запускает Gunicorn. Вывод Gunicorn сохраняется в `/logs/access_file_g.log` и `/logs/error_file_g.log` внутри Django-контейнера. Если при первом запуске база ещё не готова, проверьте вывод команд и при необходимости повторите миграции после её готовности:

```sh
docker compose exec askvk_django python manage.py migrate
```

Данные PostgreSQL, собранная статика и логи сохраняются в томах `postgres_data`, `static_data`, `django_logs` и `nginx_logs`. Каталог `media/` подключён с хоста. Загрузка аватаров пока не сохраняет файлы.

Исходники копируются в образ при сборке; volume с исходным кодом и автоматическая перезагрузка не настроены. После изменения Python-кода или шаблонов повторите:

## Статика

- `static/` — исходные CSS, JS и favicon; папка указана в `STATICFILES_DIRS`.
- `static_temp/` — результат `collectstatic`, заданный в `STATIC_ROOT`.
- Шаблоны используют `{% load static %}` и `{% static '...' %}` для построения URL.
- В Docker папка `/app/static_temp` Django и `/static` nginx подключены к общему тому `static_data`. Поэтому nginx получает и файлы проекта, и собранную статику админки.

Если менялась только статика, её можно пересобрать командой `python manage.py collectstatic --noinput`. Для Docker сначала пересоберите образ с изменёнными исходниками, затем выполните `docker compose up --build -d`: сбор статики уже включён в стартовый скрипт.

В текущем `AskVK/urls.py` маршрут `/admin/` не подключён. Подключение `django.contrib.admin` в настройках само по себе не создаёт этот маршрут.

## Маршруты и страницы

| URL | Имя маршрута | View | Содержимое |
| --- | --- | --- | --- |
| `/` | `index` | `IndexView` | Список вопросов |
| `/question/1/` | `question` | `QuestionView` | Вопрос по `id`, ответы и форма ответа |
| `/ask/` | `ask` | `AskView` | Форма нового вопроса |
| `/login/` | `login` | `LoginView` | Форма входа |
| `/signup/` | `signup` | `SignupView` | Форма регистрации |
| `/profile/` | `profile` | `ProfileView` | Форма настроек тестового профиля |

Ссылки сортировки и тегов используют общую страницу: `/?sort=new`, `/?sort=popular`, `/?tag=python`. В текущем `IndexView` эти параметры ещё не меняют выборку.

Пагинация использует `Paginator.get_page()`: при отсутствии `page` или нечисловом значении открывается первая страница; при номере вне диапазона (включая 0 и отрицательные значения) — последняя. Ссылки содержат корректные номера страниц и сохраняют остальные query-параметры. Неизвестный `id` вопроса по-прежнему возвращает HTTP 404.

## Структура

```text
AskVK/                  настройки Django и корневые маршруты
core/                   формы и view входа, регистрации и профиля
  templates/            шаблоны пользовательских страниц и общих полей
questions/              формы, view, тестовые данные и пагинация
  templates/            шаблоны вопросов и подшаблоны аватаров/голосования
templates/base.html     общий layout и сайдбар
static/                 исходная статика
static_temp/            собранная статика, исключена из Git
media/                  каталог для загружаемых файлов
nginx/                  Dockerfile и конфигурация nginx
scripts/entry.sh        запуск Django-контейнера
Dockerfile              образ Django
docker-compose.yaml     Django, PostgreSQL и nginx
requirements.txt        Python-зависимости
.env.example            пример настроек окружения
```

## Проверки

В `tests/responsive/` находится актуальный набор e2e для Django: 18 сценариев на трёх ширинах (375, 768 и 1200 px), всего 54 проверки. Тесты проверяют адаптивность, статику, маршруты, HTTP 404 для неизвестного вопроса, подстановку допустимой страницы при ошибках пагинации и POST формы вопроса с CSRF.

После установки Python-зависимостей в `.venv`:

```sh
cd tests/responsive
npm ci
npx @e2e-dev/web install chromium
npx e2e run
```

По умолчанию e2e сам запускает Django на свободных портах с временными SQLite-базами и тестовыми настройками, без чтения `.env` и доступа к PostgreSQL проекта. Для проверки уже запущенного приложения через nginx:

```sh
E2E_BASE_URL=http://localhost npx e2e run
```

ИИ-сценарий через ChatGPT (`gpt-6-luna`) обновлён под Django, но запускается только отдельно и вручную. Подробности, команды и расположение отчётов — в [tests/responsive/README.md](tests/responsive/README.md).
