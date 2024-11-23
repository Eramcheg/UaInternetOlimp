from django.contrib.auth.backends import ModelBackend
from shop.forms import User


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Пытаемся найти пользователя либо по email, либо по username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        # Проверяем пароль
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None