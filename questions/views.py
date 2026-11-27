from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import InvalidPage, Page, Paginator
from django.http import Http404, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.csrf import csrf_failure as default_csrf_failure
from django.views.generic import FormView, TemplateView, View

from .forms import AcceptedAnswerForm, AnswerForm, QuestionForm, VoteForm
from .models import Answer, Question, Tag


def paginate(objects_list: list, request: HttpRequest, per_page: int = 10) -> Page:
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except InvalidPage:
        page = paginator.page(1)
    page.visible_numbers = paginator.get_elided_page_range(page.number)
    return page


class IndexView(TemplateView):
    template_name = 'index.html'
    questions_per_page = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = Question.objects.new(self.request.user)

        context['page_obj'] = paginate(questions_list, self.request, self.questions_per_page)

        return context


class AskView(LoginRequiredMixin, FormView):
    template_name = 'ask.html'
    form_class = QuestionForm

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'author': self.request.user}

    def form_valid(self, form):
        return HttpResponseRedirect(form.save().get_absolute_url())


class QuestionView(FormView):
    template_name = 'question.html'
    form_class = AnswerForm
    answers_per_page = 30

    @cached_property
    def question(self) -> Question:
        return get_object_or_404(Question.objects.for_display(self.request.user), pk=self.kwargs['id'])

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'question': self.question, 'author': self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        answers = Answer.objects.get_by_question(self.question, self.request.user)

        context.update({
            'question': self.question,
            'can_mark_answer': self.request.user.pk == self.question.author_id,
            'page_obj': paginate(answers, self.request, self.answers_per_page),
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        answer = form.save()
        page = Answer.objects.page_for(answer, self.answers_per_page)
        url = self.question.get_absolute_url()
        if page > 1:
            url += f'?page={page}'
        return HttpResponseRedirect(f'{url}#answer-{answer.pk}')


class HotView(TemplateView):
    template_name = 'hot.html'
    questions_per_page = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = Question.objects.hot(self.request.user)

        context['page_obj'] = paginate(questions_list, self.request, self.questions_per_page)

        return context


class TagView(TemplateView):
    template_name = 'tag.html'
    questions_per_page = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, name=self.kwargs['tag'])
        context['tag'] = tag

        questions_list = Question.objects.by_tag(tag.name, self.request.user)

        context['page_obj'] = paginate(questions_list, self.request, self.questions_per_page)

        return context


def csrf_failure(request, reason=''):
    match = request.resolver_match
    if match and match.namespace == 'question_actions':
        return JsonResponse(
            {'error': 'Не удалось подтвердить запрос. Обновите страницу и попробуйте снова.'},
            status=403,
        )
    return default_csrf_failure(request, reason=reason)


class QuestionActionView(View):
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and not request.user.is_authenticated:
            return JsonResponse({'error': 'Войдите, чтобы выполнить это действие.'}, status=401)
        try:
            return super().dispatch(request, *args, **kwargs)
        except (Http404, ObjectDoesNotExist):
            return JsonResponse({'error': 'Публикация не найдена.'}, status=404)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse(
            {'error': 'Для этого действия нужен POST-запрос.'},
            status=405,
            headers={'Allow': 'POST'},
        )

    def submit(self, form):
        if not form.is_valid():
            errors = [str(message) for messages in form.errors.values() for message in messages]
            return JsonResponse({'error': ' '.join(errors)}, status=400)
        return JsonResponse(form.save())


class VoteView(QuestionActionView):
    model = None

    def post(self, request, id):
        target = get_object_or_404(self.model, pk=id)
        return self.submit(VoteForm(request.POST, target=target, user=request.user))


class AcceptedAnswerView(QuestionActionView):
    def post(self, request, id):
        question = get_object_or_404(Question, pk=id)
        if question.author_id != request.user.pk:
            return JsonResponse({'error': 'Только автор вопроса может выбрать правильный ответ.'}, status=403)
        return self.submit(AcceptedAnswerForm(request.POST, question=question))
