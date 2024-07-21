from django.contrib import admin
from django_ckeditor_5.widgets import CKEditor5Widget
from shop.models import User, Article
from django import forms

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff')

class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(config_name='extends'),
        }

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm