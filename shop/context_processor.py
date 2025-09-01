from django.urls import reverse

from shop.views import current_tour, get_user_role


def get_current_tour(request):
    return {'current_tour': current_tour}


def user_role(request):
    return {'role':get_user_role(request.user.email)}
