from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _

from shop.models import Banner

User = get_user_model()

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['image']
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label = ("Email"),
        max_length = 254,
        widget = forms.EmailInput(attrs={'autocomplete' : 'email'})
    )
    first_name = forms.CharField(label="First Name", max_length=30, required=True)
    last_name = forms.CharField(label="Last Name", max_length=30, required=True)
    birthdate = forms.CharField(label="Birthdate", max_length=30, required=False)
    receive_newsletter = forms.BooleanField(label="Sign up for our newsletter", required=False)
    offers = forms.BooleanField(label="Receive offers from our partners", required=False)
    SOCIAL_TITLE_CHOICES = [
        (1, "Mr."),
        (2, "Mrs."),
    ]
    social_title = forms.ChoiceField(
        choices=SOCIAL_TITLE_CHOICES,
        widget=forms.RadioSelect,
        label="Social title",
        required=False
    )
    class Meta(UserCreationForm.Meta):
        model =User
        fields = ("social_title", "first_name", "last_name",  "email","birthdate", "offers", "receive_newsletter")