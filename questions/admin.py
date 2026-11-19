from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Question, Tag, Answer, QuestionVote, AnswerVote


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', )
    search_fields = ('name', )
    list_filter = ('created_at', )


class AnswerInline(admin.TabularInline):
    model = Answer
    autocomplete_fields = ('author',)
    extra = 0

    def get_queryset(self, request: HttpRequest) -> QuerySet[Answer]:
        return super().get_queryset(request).select_related('question', 'author')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'text', 'tag_names', 'created_at')
    search_fields = ('title', 'text', 'author__username', 'author__email')
    list_filter = ('created_at', 'tags', 'author', )
    list_select_related = ('author', )
    inlines = (AnswerInline,)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        return super().get_queryset(request).prefetch_related('tags')

    @admin.display(description='Теги')
    def tag_names(self, question: Question) -> str | None:
        return ', '.join(tag.name for tag in question.tags.all()) or None

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'text', 'is_accepted', 'created_at')
    search_fields = ('text', 'author__username', 'author__email', 'question__title')
    list_filter = ('created_at', 'question', 'author', 'is_accepted')
    ordering = ('-pk',)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Answer]:
        return super().get_queryset(request).select_related('author', 'question')

@admin.register(QuestionVote)
class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'value', 'created_at')
    search_fields = ('question__title', 'user__username', 'user__email')
    list_filter = ('created_at', 'question', 'user')
    list_select_related = ('question', 'user')

@admin.register(AnswerVote)
class AnswerVoteAdmin(admin.ModelAdmin):
    list_display = ('answer', 'user', 'value', 'created_at')
    search_fields = ('answer__text', 'user__username', 'user__email')
    list_filter = ('created_at', 'value', 'user')
    list_select_related = ('answer__question', 'answer__author', 'user')
    autocomplete_fields = ('answer',)
