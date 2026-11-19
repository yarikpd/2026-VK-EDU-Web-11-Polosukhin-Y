from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse


class TagManager(models.Manager['Tag']):
    def popular(self) -> models.QuerySet['Tag']:
        return self.get_queryset().annotate(
            question_count=models.Count('questions'),
        ).filter(question_count__gt=0).order_by('-question_count', 'name')


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

    objects = TagManager()

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.name


class QuestionManager(models.Manager['Question']):
    def for_display(self) -> models.QuerySet['Question']:
        vote_totals = (
            QuestionVote.objects.filter(question_id=models.OuterRef('pk'))
            .values('question_id')
            .annotate(total=models.Sum('value', output_field=models.IntegerField()))
            .values('total')
        )
        return self.get_queryset().select_related('author__profile').prefetch_related('tags').annotate(
            answers_count=models.Count('answers'),
            rating=Coalesce(models.Subquery(vote_totals), 0),
        )

    def new(self) -> models.QuerySet['Question']:
        return self.for_display().order_by('-created_at', '-pk')

    def hot(self) -> models.QuerySet['Question']:
        return self.new().order_by('-rating', '-created_at', '-pk')

    def by_tag(self, tag_name: str) -> models.QuerySet['Question']:
        return self.new().filter(tags__name=tag_name)


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

    objects = QuestionManager()

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('question', kwargs={'id': self.pk})

class AnswerManager(models.Manager['Answer']):
    def get_by_question(self, question: Question) -> models.QuerySet['Answer']:
        return self.get_queryset().select_related('author__profile').annotate(
            rating=models.Sum('votes__value', default=0),
        ).filter(question=question).order_by('-is_accepted', '-rating', '-created_at', '-pk')

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
    is_accepted = models.BooleanField(
        'Принял ли ответ автор',
        default=False
    )
    created_at = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    objects = AnswerManager()

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
        constraints = [
            models.UniqueConstraint(
                fields=('question',),
                condition=models.Q(is_accepted=True),
                name='question_only_one_correct',
            ),
        ]

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
