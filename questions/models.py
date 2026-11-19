from django.conf import settings
from django.db import models

class Tag(models.Model):
    name = models.CharField(
        'название тега',
        max_length=30,
        unique=True,
        help_text='Введите название тега.',
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.name

class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='автор',
    )
    title = models.CharField(
        'заголовок',
        max_length=150,
        help_text='Введите заголовок вопроса.',
    )
    text = models.TextField(
        'текст вопроса',
        max_length=10000,
        help_text='Введите текст вопроса.',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='questions',
        verbose_name='теги',
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='вопрос',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='автор',
    )
    text = models.TextField(
        'текст ответа',
        max_length=10000,
        help_text='Введите текст ответа.',
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'

    def __str__(self) -> str:
        return f'Ответ на вопрос "{self.question.title}" от {self.author.get_username()}'

class QuestionVote(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='вопрос',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='question_votes',
        verbose_name='пользователь',
    )
    value = models.SmallIntegerField(
        'значение голоса',
        choices=((1, 'За'), (-1, 'Против')),
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'голос за вопрос'
        verbose_name_plural = 'голоса за вопросы'
        unique_together = ('question', 'user')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=(-1, 1)),
                name='question_vote_value_plus_or_minus_one',
            ),
        ]

    def __str__(self) -> str:
        return f'Голос {self.get_value_display()} от {self.user.get_username()} за вопрос "{self.question.title}"'

class AnswerVote(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='ответ',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answer_votes',
        verbose_name='пользователь',
    )
    value = models.SmallIntegerField(
        'значение голоса',
        choices=((1, 'За'), (-1, 'Против')),
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'голос за ответ'
        verbose_name_plural = 'голоса за ответы'
        unique_together = ('answer', 'user')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=(-1, 1)),
                name='answer_vote_value_plus_or_minus_one',
            ),
        ]

    def __str__(self) -> str:
        return f'Голос {self.get_value_display()} от {self.user.get_username()} за ответ на вопрос "{self.answer.question.title}"'
