"""Изолированный Django-сервер для e2e; настройки приложения на диске не меняет."""
import os
from pathlib import Path
import secrets
import signal
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE'] = 'AskVK.settings'

import django
from django.conf import settings
from django.core.management import call_command


def main():
    port = int(sys.argv[1])
    with TemporaryDirectory(prefix='askvk-e2e-') as directory:
        settings.SECRET_KEY = secrets.token_urlsafe(50)
        settings.DEBUG = True
        settings.ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']
        settings.DATABASES = {
            'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': str(Path(directory) / 'test.sqlite3')},
        }
        settings.MEDIA_ROOT = Path(directory) / 'media'
        django.setup()
        call_command('migrate', interactive=False, verbosity=0)
        call_command('runserver', f'127.0.0.1:{port}', use_reloader=False)


if __name__ == '__main__':
    # Runner останавливает сервер через SIGTERM; выходим через finally,
    # чтобы TemporaryDirectory удалил тестовую БД и media.
    def stop(signum, frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    main()
