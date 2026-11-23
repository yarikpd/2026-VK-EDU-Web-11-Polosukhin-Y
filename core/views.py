from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, UpdateView

from .forms import LoginForm, ProfileForm, SignupForm


class LoginView(DjangoLoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    next_page = 'index'


class LogoutView(LoginRequiredMixin, DjangoLogoutView):
    next_page = 'index'

    def get_redirect_url(self, request=None):
        target = super().get_redirect_url(request)
        current_request = request or self.request
        return '' if target == current_request.get_full_path() else target


@method_decorator(sensitive_post_parameters(), name='dispatch')
class SignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        login(self.request, form.save())
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return get_user_model().objects.select_related('profile').get(pk=self.request.user.pk)
