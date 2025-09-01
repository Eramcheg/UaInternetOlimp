import re

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import Form
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Widget

from shop.models import Banner, Article

User = get_user_model()

OBLAST_CHOICES = [
    ("", "— Оберіть область —"),
    ("24", "Вінницька"), ("07", "Волинська"), ("12", "Дніпропетровська"),
    ("14", "Донецька"), ("18", "Житомирська"), ("21", "Закарпатська"),
    ("23", "Запорізька"), ("26", "Івано-Франківська"), ("32", "Київська"),
    ("35", "Кіровоградська"), ("44", "Луганська"), ("46", "Львівська"),
    ("48", "Миколаївська"), ("51", "Одеська"), ("53", "Полтавська"),
    ("56", "Рівненська"), ("59", "Сумська"), ("61", "Тернопільська"),
    ("63", "Харківська"), ("65", "Херсонська"), ("68", "Хмельницька"),
    ("71", "Черкаська"), ("73", "Чернівецька"), ("74", "Чернігівська"),
    ("80", "м. Київ")
]

PARALEL_CHOICES = [("8", "8"), ("9", "9"), ("10", "10"), ("11", "11")]
GROUP_CHOICES = [
    ("beginner", "Базова"),
    ("advanced", "Поглиблена"),
]

OLYMPIAD_SUBJECTS = [
    ("physics", "Фізика"),
    ("astronomy", "Астрономія"),
]

phone_validator = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message="Введіть телефон у форматі +380XXXXXXXXX (9–15 цифр)."
)


def ua_phone_validator(value: str):
    digits = re.sub(r'\D+', '', value or '')
    if digits.startswith('0') and len(digits) == 10:
        digits = '38' + digits
    if not (digits.startswith('380') and len(digits) == 12):
        raise ValidationError("Введіть телефон у форматі +38 (0XX) XXX-XX-XX")


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


class SchoolRegistrationForm(Form):
    lastName_uk = forms.CharField(label="Прізвище (укр)", max_length=60)
    firstName_uk = forms.CharField(label="Ім’я (укр)", max_length=60)
    patronymic_uk = forms.CharField(label="По батькові (укр)", max_length=60, required=True)

    lastName_en = forms.CharField(label="Прізвище (лат.)", max_length=60)
    firstName_en = forms.CharField(label="Ім’я (лат.)", max_length=60)
    # patronymic_en = forms.CharField(label="По батькові (лат.)", max_length=60, required=False)

    studyInUkraine = forms.BooleanField(
        label="Навчаюсь в Україні", required=False, initial=False
    )
    schoolOblast = forms.ChoiceField(label="Область школи (якщо в Україні)",
                                     choices=OBLAST_CHOICES, required=False)
    schoolNumber = forms.CharField(label="Номер школи (якщо в Україні)",
                                   max_length=30, required=False)
    schoolName = forms.CharField(label="Назва школи (необов’язково)",
                                 max_length=120, required=False)

    residenceCity = forms.CharField(label="Місто проживання", max_length=80)
    residenceCountry = forms.CharField(label="Країна проживання", max_length=80)

    contactEmail = forms.EmailField(label="Е-мейл для зв’язку")

    paralel = forms.ChoiceField(label="Паралель", choices=PARALEL_CHOICES)

    olympiadsParticipation = forms.BooleanField(
        label="Беру участь в олімпіадах", required=False
    )
    olympiadsAchievements = forms.CharField(
        label="Досягнення (коротко)",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=True
    )

    plannedGroup = forms.ChoiceField(label="Група навчання", choices=GROUP_CHOICES)

    contactLinks = forms.CharField(
        label="Посилання на соцмережі / месенджери (по одному у рядку)",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=True
    )

    npRecipientFullName = forms.CharField(label="ПІБ отримувача (НП)", max_length=90)
    npPhone = forms.CharField(
        label="Телефон отримувача (НП)",
        validators=[ua_phone_validator]
    )

    npCity = forms.CharField(label="Місто (НП)", max_length=80)
    npBranchNumber = forms.CharField(label="№ відділення НП", max_length=20)

    consentGiven = forms.BooleanField(label="Згоден(-на) з наданням персональної інформації")

    def clean(self):
        cleaned = super().clean()
        # Якщо «навчаюсь в Україні» — область і номер школи обов’язкові
        if cleaned.get("studyInUkraine"):
            if not cleaned.get("schoolOblast"):
                self.add_error("schoolOblast", "Вкажіть область.")
            if not cleaned.get("schoolNumber"):
                self.add_error("schoolNumber", "Вкажіть номер школи.")
        # Якщо участь в олімпіадах — щонайменше предмет або опис
        # Згода обов’язкова (поле й так required=True, але дублюємо перевірку)
        if not cleaned.get("consentGiven"):
            self.add_error("consentGiven", "Потрібна згода на обробку персональних даних.")
        return cleaned



class ArticleForm(forms.ModelForm):
    article_content = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'))  # Ensure this is correctly referenced

    class Meta:
        model = Article
        fields = ['article_name', 'article_content', 'mini_article_photo', 'mini_article_name', 'mini_article_text']
