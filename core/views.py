from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import FormView

from core.forms import LoginForm, ProfileForm, SignupForm
from questions.mixins import SidebarContextMixin


class AccountFormView(SidebarContextMixin, FormView):
    def form_valid(self, form):
        # TODO: Implement DB
        return self.render_to_response(
            self.get_context_data(form=form, submission_checked=True)
        )


class LoginView(AccountFormView):
    template_name = 'login.html'
    form_class = LoginForm
    extra_context = {
        'page_title': 'Вход',
        'submit_label': 'Войти',
        'error_message': 'Не удалось войти. Исправьте отмеченные поля.',
        'checked_message': 'Данные проверены. Авторизация пока не подключена.',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.POST.get('next') or self.request.GET.get('next', '')
        context['next_url'] = next_url if url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ) else reverse('index')
        return context


class SignupView(AccountFormView):
    template_name = 'signup.html'
    form_class = SignupForm
    extra_context = {
        'page_title': 'Регистрация',
        'submit_label': 'Зарегистрироваться',
        'error_message': 'Не удалось создать аккаунт. Исправьте отмеченные поля.',
        'checked_message': 'Данные проверены. Создание аккаунта и сохранение аватара пока не подключены.',
    }


class ProfileView(AccountFormView):
    template_name = 'profile.html'
    form_class = ProfileForm
    extra_context = {
        'page_title': 'Настройки профиля',
        'submit_label': 'Сохранить',
        'error_message': 'Изменения не сохранены. Исправьте отмеченные поля.',
        'checked_message': 'Данные проверены. Сохранение профиля и аватара пока не подключено.',
    }

    def get_profile(self):
        # TODO: Implement DB
        return {
            'firstname': 'Ярослав',
            'lastname': 'Полосухин',
            'initials': 'ЯП',
            'avatar_color': '#70545e',
            'email': 'yaroslav@example.com',
            'nickname': 'yaroslav',
        }

    def get_initial(self):
        initial = super().get_initial()
        profile = self.get_profile()
        initial.update(email=profile['email'], nickname=profile['nickname'])
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context
