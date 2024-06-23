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