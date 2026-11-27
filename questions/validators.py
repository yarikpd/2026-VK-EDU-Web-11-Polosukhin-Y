from unicodedata import category
from urllib.parse import unquote, urlsplit

from django.core.exceptions import ValidationError
from django.urls import NoReverseMatch, Resolver404, get_script_prefix, resolve, reverse


def validate_tag_name(name):
    if any(category(char) == 'Cc' for char in name):
        raise ValidationError('Тег не может содержать управляющие символы.')
    if any(part in ('', '.', '..') for part in name.split('/')) or '\\' in name:
        raise ValidationError('Название тега содержит недопустимую часть пути.')
    try:
        url = reverse('tag', kwargs={'tag': name})
        path = unquote(urlsplit(url).path.removeprefix(get_script_prefix()))
        match = resolve('/' + path)
        if match.url_name == 'tag' and match.kwargs.get('tag') == name:
            return
    except (NoReverseMatch, Resolver404):
        pass
    raise ValidationError('Для этого тега нельзя построить ссылку.')
