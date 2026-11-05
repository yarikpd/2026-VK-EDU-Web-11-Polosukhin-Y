from django.contrib.auth.views import redirect_to_login
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from questions.forms import AnswerForm, QuestionForm
from questions.mixins import SidebarContextMixin
from questions.services import get_answers, get_questions


def get_pagination_context(request, objects_list, objects_per_page, fragment=''):
    paginator = Paginator(objects_list, objects_per_page)
    try:
        current_page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        raise Http404('Некорректный номер страницы')

    try:
        page = paginator.page(current_page)
    except InvalidPage:
        raise Http404('Страница не найдена')

    query_params = request.GET.copy()
    path = request.get_full_path().split('?', 1)[0]

    def page_url(number):
        query_params['page'] = str(number)
        anchor = f'#{fragment}' if fragment else ''
        return f'{path}?{query_params.urlencode()}{anchor}'

    return {
        'objects_list': page.object_list,
        'current_page': page.number,
        'pages_list': [
            {'number': number, 'url': page_url(number)}
            for number in paginator.page_range
        ],
        'has_previous': page.has_previous(),
        'previous_page_url': page_url(page.previous_page_number()) if page.has_previous() else None,
        'has_next': page.has_next(),
        'next_page_url': page_url(page.next_page_number()) if page.has_next() else None,
    }


class IndexView(SidebarContextMixin, TemplateView):
    template_name = 'index.html'
    questions_per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = get_questions()

        pagination = get_pagination_context(
            self.request, questions_list, self.questions_per_page
        )
        context.update({
            'questions': pagination['objects_list'],
            'pagination': pagination,
        })

        return context


class AskView(SidebarContextMixin, FormView):
    template_name = 'ask.html'
    form_class = QuestionForm

    def form_valid(self, form):
        # TODO: Implement DB
        return self.render_to_response(
            self.get_context_data(form=form, submission_checked=True)
        )


class QuestionView(SidebarContextMixin, FormView):
    template_name = 'question.html'
    form_class = AnswerForm
    answers_per_page = 5

    def get_question(self):
        for question in get_questions():
            if question['id'] == self.kwargs['id']:
                return question
        raise Http404('Вопрос не найден')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_question()
        answers = get_answers(question['id'])
        question['answers_count'] = len(answers)
        pagination = get_pagination_context(
            self.request, answers, self.answers_per_page, fragment='answers'
        )

        context.update({
            'question': question,
            'answers': pagination['objects_list'],
            'can_answer': self.request.user.is_authenticated,
            'pagination': pagination,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.get_question()
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=reverse('login'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # TODO: Implement DB
        return self.render_to_response(
            self.get_context_data(form=form, submission_checked=True)
        )
