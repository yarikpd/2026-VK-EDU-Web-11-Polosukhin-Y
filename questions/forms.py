from django import forms


class QuestionForm(forms.Form):
    title = forms.CharField(
        label='Заголовок',
        max_length=150,
        error_messages={'required': 'Введите заголовок вопроса.'},
    )
    body = forms.CharField(
        label='Текст вопроса',
        max_length=10000,
        widget=forms.Textarea,
        error_messages={'required': 'Добавьте описание вопроса.'},
    )
    tags = forms.CharField(
        label='Теги',
        max_length=94,
        error_messages={'required': 'Укажите хотя бы один тег.'},
    )

    def clean_tags(self):
        tags = [tag.strip() for tag in self.cleaned_data['tags'].split(',')]
        if not all(tags):
            raise forms.ValidationError('Укажите непустые теги через запятую.')
        if len(tags) > 3:
            raise forms.ValidationError('Можно указать не более 3 тегов.')
        if any(len(tag) > 30 for tag in tags):
            raise forms.ValidationError('Каждый тег должен содержать не более 30 символов.')
        return tags


class AnswerForm(forms.Form):
    body = forms.CharField(
        label='Текст ответа',
        max_length=10000,
        widget=forms.Textarea,
        error_messages={'required': 'Добавьте текст ответа.'},
    )
