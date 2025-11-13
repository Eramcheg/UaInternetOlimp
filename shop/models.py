import os

from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.db import models
from django.contrib.auth.models import AbstractUser
from slugify import slugify
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


class Group(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    # image = models.ImageField(upload_to="groups/", blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def _olymp_file_path(instance, filename):
    # media/olympiads/<group-slug>/<year>/<task-order-or-slug>/<filename>
    gslug = instance.olympiad.group.slug
    year = instance.olympiad.year
    order = f"{instance.order:02d}" if instance.order is not None else "x"
    return f"olympiads/{gslug}/{year}/{order}/{filename}"


class Olympiad(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="olympiads")
    name = models.CharField(max_length=160)
    year = models.PositiveIntegerField()
    # is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = (("group", "name", "year"),)
        ordering = ["-year", "name"]
        indexes = [
            models.Index(fields=["group", "year"]),
            # models.Index(fields=["is_published"]),
        ]

    def __str__(self):
        return f"{self.name} {self.year}"


class OlympiadTask(models.Model):
    olympiad = models.ForeignKey(Olympiad, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160, help_text="Назва завдання")
    order = models.PositiveIntegerField(default=1, help_text="Порядок виводу завдань")
    tasks_file = models.FileField(upload_to=_olymp_file_path, blank=True, null=True)
    solutions_file = models.FileField(upload_to=_olymp_file_path, blank=True, null=True)

    class Meta:
        ordering = ["order", "title"]
        unique_together = (("olympiad", "order"),)

    def __str__(self):
        return f"{self.olympiad}: {self.title}"


def _olymp_library_path(instance, filename):
    # instance — это объект Material
    name, ext = os.path.splitext(filename)
    title_slug = slugify(instance.title or name)

    # безопасно получаем id/slug библиотеки
    lib_part = getattr(instance.library, "slug", None) or instance.library_id or "library"

    # не полагайтесь на instance.pk — при создании его ещё может не быть
    return f"olymp/{lib_part}/{title_slug}{ext}"


class LibraryType(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Material(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    file = models.FileField(upload_to=_olymp_library_path, blank=True, null=True)
    external_url = models.URLField(blank=True)
    library = models.ForeignKey(LibraryType, on_delete=models.CASCADE, related_name="materials")

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
