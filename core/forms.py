from django import forms
from django.core.validators import FileExtensionValidator


class AccountForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            errors = self.errors.get(name) if self.is_bound else None
            field.widget.attrs['class'] = 'form-control is-invalid' if errors else 'form-control'
            described_by = []
            if field.help_text:
                described_by.append(f'{self[name].auto_id}_helptext')
            if errors:
                field.widget.attrs['aria-invalid'] = 'true'
                described_by.append(f'{self[name].auto_id}_error')
            if described_by:
                field.widget.attrs['aria-describedby'] = ' '.join(described_by)


class LoginForm(AccountForm):
    email = forms.EmailField(
        label='Электронная почта', max_length=254,
        help_text='Адрес, указанный при регистрации.',
        widget=forms.EmailInput(attrs={'autocomplete': 'username'}),
        error_messages={'required': 'Введите email.', 'invalid': 'Введите корректный email.'},
    )
    password = forms.CharField(
        label='Пароль', max_length=128, strip=False,
        help_text='Введите пароль от своей учетной записи.',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
        error_messages={'required': 'Введите пароль.'},
    )


class ProfileForm(AccountForm):
    email = forms.EmailField(
        label='Электронная почта', max_length=254,
        help_text='Используется для входа и уведомлений.',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        error_messages={'required': 'Введите email.', 'invalid': 'Введите корректный email.'},
    )
    nickname = forms.CharField(
        label='Никнейм', min_length=3, max_length=30,
        help_text='От 3 до 30 символов.',
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'minlength': 3}),
        error_messages={'required': 'Введите никнейм.'},
    )
    avatar = forms.FileField(
        label='Новый аватар', required=False,
        help_text='PNG или JPEG, до 2 МБ.',
        widget=forms.FileInput(attrs={'accept': 'image/png,image/jpeg'}),
        validators=[FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg'],
            message='Выберите файл PNG или JPEG.',
        )],
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Размер аватара не должен превышать 2 МБ.')
        return avatar


class SignupForm(ProfileForm):
    password = forms.CharField(
        label='Пароль', min_length=8, max_length=128, strip=False,
        help_text='От 8 до 128 символов.',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'minlength': 8}),
        error_messages={'required': 'Введите пароль.'},
    )
    password_repeat = forms.CharField(
        label='Повторите пароль', min_length=8, max_length=128, strip=False,
        help_text='Пароли должны совпадать.',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'minlength': 8}),
        error_messages={'required': 'Повторите пароль.'},
    )
    field_order = ['email', 'nickname', 'password', 'password_repeat', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = 'Мы используем адрес для входа в аккаунт.'
        self.fields['avatar'].label = 'Аватар'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeated = cleaned_data.get('password_repeat')
        if password and repeated and password != repeated:
            self.add_error('password_repeat', 'Пароли не совпадают.')
        return cleaned_data
