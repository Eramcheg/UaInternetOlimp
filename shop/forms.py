from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from shop.models import Banner

User = get_user_model()

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['image']
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=("Емейл"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    login = forms.CharField(label="Логін",min_length=3, max_length=9, required=True,
                            validators=[RegexValidator(
                                regex=r'^[a-zA-Z0-9]*$',
                                message='Логін повинен містити тільки букви та цифри.',
                            )]
                            )
    first_name = forms.CharField(label="Ім'я", max_length=30, required=True)
    last_name = forms.CharField(label="Прізвище", max_length=30, required=True)
    third_name = forms.CharField(label="По батькові", max_length=30, required=True)
    school = forms.CharField(label="Школа", max_length=90, required=True)
    phone_number = forms.CharField(label="Номер телефону", max_length=15, required=True)
    PARALELS = [
        (9, "9"),
        (10, "10"),
        (11, "11"),
    ]

    paralel_number = forms.ChoiceField(
        choices=PARALELS,
        label="Social title",
        required=True,
        widget=forms.Select
    )
    error_messages = {
        'password_mismatch': 'Паролі не співпадають.',
        'password_too_short': 'Пароль занадто короткий. Мінімум 8 символів.',
        'password_too_common': 'Пароль занадто простий.',
        'password_entirely_numeric': 'Пароль не може складатися лише з цифр.',
    }
    class Meta(UserCreationForm.Meta):
        model =User
        fields = ("login", "first_name", "last_name", "third_name", "email", "school", "paralel_number", "phone_number")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
        return password2