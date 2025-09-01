from django.urls import reverse

from shop.views import current_tour, get_user_role, get_user_session_type


def get_current_tour(request):
    return {'current_tour': current_tour}


def user_role(request):
    return {'role': get_user_role(get_user_session_type(request))}
