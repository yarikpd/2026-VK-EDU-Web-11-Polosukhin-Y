from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, Page
from django.http import Http404, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from questions.forms import AnswerForm, QuestionForm
from questions.services import get_answers, get_questions, get_popular_tags, Question


def paginate(objects_list: list, request: HttpRequest, per_page: int = 10) -> Page:
    paginator = Paginator(objects_list, per_page)
    return paginator.get_page(request.GET.get('page', 1))


class IndexView(TemplateView):
    template_name = 'index.html'
    questions_per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = get_questions()

        context['page_obj'] = paginate(questions_list, self.request, self.questions_per_page)

        return context


class AskView(FormView):
    template_name = 'ask.html'
    form_class = QuestionForm

    def form_valid(self, form):
        # TODO: Implement DB
        return self.render_to_response(
            self.get_context_data(form=form, submission_checked=True)
        )


class QuestionView(FormView):
    template_name = 'question.html'
    form_class = AnswerForm
    answers_per_page = 5

    def get_question(self) -> Question:
        for question in get_questions():
            if question['id'] == self.kwargs['id']:
                return question
        raise Http404('Вопрос не найден')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_question()
        answers = get_answers(question['id'])
        question['answers_count'] = len(answers)

        context.update({
            'question': question,
            'can_answer': self.request.user.is_authenticated,
            'page_obj': paginate(answers, self.request, self.answers_per_page),
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

class HotView(TemplateView):
    template_name = 'hot.html'
    questions_per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = get_questions()

        context['page_obj'] = paginate(questions_list, self.request, self.questions_per_page)

        return context

class TagView(TemplateView):
    template_name = 'tag.html'
    questions_per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_name = self.kwargs['tag']

        # TODO: Implement DB
        tags = get_popular_tags()
        for tag in tags:
            if tag['id'] == tag_name:
                context['tag'] = tag
                break

        questions_list = get_questions()

        context['page_obj'] = paginate(questions_list, self.request, self.questions_per_page)

        return context

class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('index'))