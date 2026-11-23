from django import forms
from django.db import transaction
from django.db.models import Sum

from .models import Answer, Question, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        max_length=94,
        help_text='Не более 3 тегов через запятую. До 30 символов в каждом.',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        help_texts = {
            'title': 'Кратко сформулируйте вопрос. Не более 150 символов.',
            'text': 'Опишите задачу, ожидаемый результат и то, что уже пробовали. До 10 000 символов.',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

    def __init__(self, *args, author, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.author_id = author.pk

    def clean_tags(self) -> list[str]:
        tags = [tag.strip() for tag in self.cleaned_data['tags'].split(',')]
        if not all(tags):
            raise forms.ValidationError('Укажите непустые теги через запятую.')
        if len(tags) > 3:
            raise forms.ValidationError('Можно указать не более 3 тегов.')
        if any(len(tag) > 30 for tag in tags):
            raise forms.ValidationError('Каждый тег должен содержать не более 30 символов.')
        if any(part in ('.', '..') for tag in tags for part in tag.split('/')):
            raise forms.ValidationError('Теги не могут содержать отдельные части «.» или «..».')
        return list(dict.fromkeys(tags))

    @transaction.atomic
    def save(self, commit=True):
        return super().save(commit=commit)

    def _save_m2m(self):
        super()._save_m2m()
        tags = [Tag.objects.get_or_create(name=name)[0] for name in sorted(self.cleaned_data['tags'])]
        self.instance.tags.set(tags)


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        help_texts = {'text': 'До 10 000 символов. Объясните, почему ваше решение помогает.'}
        widgets = {'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})}

    def __init__(self, *args, question, author, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.question = question
        self.instance.author_id = author.pk


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(
        choices=(('1', 'За'), ('-1', 'Против'), ('0', 'Сбросить')),
        coerce=int,
    )

    def __init__(self, *args, target, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.user = user

    @transaction.atomic
    def save(self):
        target = type(self.target).objects.select_for_update().get(pk=self.target.pk)
        value = self.cleaned_data['value']
        if value:
            target.votes.update_or_create(user=self.user, defaults={'value': value})
        else:
            target.votes.filter(user=self.user).delete()
        rating = target.votes.aggregate(total=Sum('value', default=0))['total']
        return {'rating': rating, 'value': value}


class AcceptedAnswerForm(forms.Form):
    answer_id = forms.IntegerField(min_value=1, max_value=2**63 - 1)
    accepted = forms.TypedChoiceField(
        choices=(('1', 'Отметить'), ('0', 'Снять отметку')),
        coerce=lambda value: value == '1',
    )

    def __init__(self, *args, question, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question

    def clean_answer_id(self):
        answer_id = self.cleaned_data['answer_id']
        if not self.question.answers.filter(pk=answer_id).exists():
            raise forms.ValidationError('Этот ответ не относится к вопросу.')
        return answer_id

    @transaction.atomic
    def save(self):
        question = Question.objects.select_for_update().get(pk=self.question.pk)
        answer = question.answers.select_for_update().get(pk=self.cleaned_data['answer_id'])
        accepted = self.cleaned_data['accepted']
        if accepted:
            question.answers.filter(is_accepted=True).exclude(pk=answer.pk).update(is_accepted=False)
        if answer.is_accepted != accepted:
            answer.is_accepted = accepted
            answer.save(update_fields=['is_accepted'])
        return {'accepted_answer_id': question.answers.filter(is_accepted=True).values_list('pk', flat=True).first()}
