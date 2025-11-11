import re
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import Form, inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Widget

from shop.models import Banner, Article, Olympiad, Group, OlympiadTask, Material

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
BOOL_CHOICES = (('true', 'Так'), ('false', 'Ні'))
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

    studyInUkraine = forms.TypedChoiceField(
        label="Ви навчаєтесь в Україні?",
        choices=BOOL_CHOICES,
        coerce=lambda v: v == 'true',
        widget=forms.RadioSelect,
        required=True,
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

    olympiadsParticipation = forms.TypedChoiceField(
        label="Чи брали Ви участь в олімпіадах з Фізики/Астрономії?",
        choices=BOOL_CHOICES,
        coerce=lambda v: v == 'true',
        widget=forms.RadioSelect,
        required=True,
    )

    olympiadsAchievements = forms.CharField(
        label="Досягнення (коротко)",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )

    contactLinks = forms.CharField(
        label="Посилання на соцмережі / месенджери (по одному у рядку)",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=True
    )

    consentGiven = forms.TypedChoiceField(
        label="Згоден(-на) з наданням персональної інформації",
        choices=BOOL_CHOICES,
        coerce=lambda v: v == 'true',
        widget=forms.RadioSelect,
        required=True,
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("studyInUkraine"):
            if not cleaned.get("schoolOblast"):
                self.add_error("schoolOblast", "Вкажіть область.")
            if not cleaned.get("schoolNumber"):
                self.add_error("schoolNumber", "Вкажіть номер школи.")
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


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["title", "description"]


class OlympiadForm(forms.ModelForm):
    class Meta:
        model = Olympiad
        fields = ["name", "year"]

    def clean_year(self):
        y = self.cleaned_data["year"]
        if y < 1950 or y > date.today().year + 1:
            raise forms.ValidationError("Рік повинен бути в діапазоні від 1950 до наступного року")
        return y


class OlympiadTaskForm(forms.ModelForm):
    class Meta:
        model = OlympiadTask
        fields = ['order', 'title', 'tasks_file', 'solutions_file']

    def clean(self):
        cleaned = super().clean()
        tasks = cleaned.get('tasks_file')         # File OR False (if "clear" checked) OR None
        sols  = cleaned.get('solutions_file')

        cleared_tasks = (tasks is False)
        cleared_sols  = (sols is False)

        has_new = (tasks and tasks is not False) or (sols and sols is not False)
        has_existing = (
            self.instance and self.instance.pk and (
                (self.instance.tasks_file and not cleared_tasks) or
                (self.instance.solutions_file and not cleared_sols)
            )
        )

        if not (has_new or has_existing):
            raise forms.ValidationError("Потрібно прикріпити хоча б один файл (завдання або розв'язки).")

        return cleaned



class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'file']

    def clean(self):
        cleaned = super().clean()
        f = cleaned.get('file')

        has_existing = bool(getattr(self.instance, 'file', None))

        if (f in (None, False)) and not has_existing:
            raise forms.ValidationError("Потрібно прикріпити хоча б один файл.")

        return cleaned


TaskFormSet = inlineformset_factory(
    parent_model=Olympiad,
    model=OlympiadTask,
    form=OlympiadTaskForm,
    fields=["title", "order", "tasks_file", "solutions_file"],
    extra=0,
    can_delete=True,
)