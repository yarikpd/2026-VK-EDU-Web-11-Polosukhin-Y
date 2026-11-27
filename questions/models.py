from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse

from .validators import validate_tag_name


def with_user_vote(queryset, votes, user):
    if user is None or not user.is_authenticated:
        return queryset
    value = votes.filter(user=user).values('value')
    return queryset.annotate(user_vote=Coalesce(models.Subquery(value), 0))


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
        validators=[validate_tag_name],
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
    def for_display(self, user=None) -> models.QuerySet['Question']:
        votes = QuestionVote.objects.filter(question_id=models.OuterRef('pk'))
        answer_counts = Answer.objects.filter(question_id=models.OuterRef('pk')).values(
            'question_id'
        ).annotate(total=models.Count('*')).values('total')
        queryset = self.get_queryset().select_related('author__profile').prefetch_related('tags').annotate(
            answers_count=Coalesce(models.Subquery(answer_counts), 0),
        )
        return with_user_vote(queryset, votes, user)

    def new(self, user=None) -> models.QuerySet['Question']:
        return self.for_display(user).order_by('-created_at', '-pk')

    def hot(self, user=None) -> models.QuerySet['Question']:
        return self.for_display(user).order_by('-rating', '-created_at', '-pk')

    def by_tag(self, tag_name: str, user=None) -> models.QuerySet['Question']:
        return self.hot(user).filter(tags__name=tag_name)


class Question(models.Model):
    rating = models.IntegerField(default=0, editable=False)
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
        indexes = [
            models.Index(fields=['-created_at', '-id'], name='question_new_idx'),
            models.Index(fields=['-rating', '-created_at', '-id'], name='question_hot_idx'),
        ]
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('question', kwargs={'id': self.pk})

class AnswerManager(models.Manager['Answer']):
    def get_by_question(self, question: Question, user=None) -> models.QuerySet['Answer']:
        queryset = self.get_queryset().select_related('author__profile').annotate(
            rating=models.Sum('votes__value', default=0),
        ).filter(question=question).order_by('-is_accepted', '-rating', '-created_at', '-pk')
        votes = AnswerVote.objects.filter(answer_id=models.OuterRef('pk'))
        return with_user_vote(queryset, votes, user)

    def page_for(self, answer: 'Answer', per_page: int) -> int:
        answer_ids = self.get_by_question(answer.question).values_list('pk', flat=True)
        for position, answer_id in enumerate(answer_ids.iterator()):
            if answer_id == answer.pk:
                return position // per_page + 1
        raise self.model.DoesNotExist(f'Ответ с ID {answer.pk} не найден.')

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
