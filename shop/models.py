from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="%(app_label)s_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="%(app_label)s_user_set",
        related_query_name="user",
    )

    class Meta:
        app_label = 'shop'


class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='imgs/')
    priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        app_label = 'shop'
    def __str__(self):
        return self.title

class Article(models.Model):
    article_name = models.CharField(max_length=200, verbose_name="Article Name")
    article_content = CKEditor5Field('Article Content', config_name='extends', default='')
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    mini_article_photo = models.ImageField(upload_to='mini_articles_photos/', verbose_name="Mini Article Photo")
    mini_article_name = models.CharField(max_length=200, verbose_name="Mini Article Name")
    priority = models.IntegerField(default=0)
    mini_article_text = models.TextField(verbose_name="Mini Article Text")

    def save(self, *args, **kwargs):
        if not self.slug:  # Check if the slug is already set
            self.slug = slugify(self.article_name)
            base_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f'{base_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.article_name

