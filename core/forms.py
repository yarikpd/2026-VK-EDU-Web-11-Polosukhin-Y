from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.db import transaction

from .models import Profile

User = get_user_model()


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class AvatarField(forms.ImageField):
    formats = {'.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG'}

    def __init__(self, label):
        super().__init__(
            label=label,
            required=False,
            help_text='PNG или JPEG, до 2 МБ.',
            widget=forms.FileInput(attrs={'accept': 'image/png,image/jpeg'}),
        )

    def to_python(self, data):
        if not data:
            return super().to_python(data)
        if data.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Размер аватара не должен превышать 2 МБ.')
        expected_format = self.formats.get(Path(data.name).suffix.lower())
        if not expected_format:
            raise forms.ValidationError('Выберите файл PNG или JPEG.')
        image = super().to_python(data)
        if image.image.format != expected_format:
            raise forms.ValidationError('Содержимое файла должно соответствовать формату PNG или JPEG.')
        return image


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = UsernameField(
        label='Логин или электронная почта',
        max_length=254,
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'autofocus': True}),
    )
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Неверный логин, электронная почта или пароль.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].max_length = 254
        self.fields['username'].widget.attrs['maxlength'] = 254

    def clean(self):
        identifier = self.cleaned_data.get('username')
        if identifier and '@' in identifier and not User.objects.filter(username=identifier).exists():
            matches = list(User.objects.filter(email__iexact=identifier).values_list('username', flat=True)[:2])
            if len(matches) == 1:
                self.cleaned_data['username'] = matches[0]
        return super().clean()


class UserDetailsMixin(BootstrapFormMixin):
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот адрес уже используется.', code='duplicate')
        return email


class SignupForm(UserDetailsMixin, UserCreationForm):
    email = forms.EmailField(label='Электронная почта', max_length=254)
    first_name = forms.CharField(label='Имя', max_length=150)
    avatar = AvatarField(label='Аватар')

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'first_name')
        labels = {'username': 'Логин (никнейм)'}

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user, avatar=self.cleaned_data['avatar'] or '')
        return user


class ProfileForm(UserDetailsMixin, forms.ModelForm):
    email = forms.EmailField(label='Электронная почта', max_length=254)
    avatar = AvatarField(label='Новый аватар')

    class Meta:
        model = User
        fields = ('email', 'username')
        field_classes = {'username': UsernameField}
        labels = {'username': 'Никнейм'}

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот никнейм уже занят.', code='duplicate')
        return username

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = Profile.objects.get_or_create(user=user)
            if avatar := self.cleaned_data['avatar']:
                profile.avatar = avatar
                profile.save(update_fields=['avatar'])
        return user
