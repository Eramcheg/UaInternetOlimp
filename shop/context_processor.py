from django.urls import reverse

from shop.views import current_tour, get_user_role, get_user_session_type, current_year


def get_current_tour(request):
    return {'current_tour': current_tour}


def get_current_year(request):
    return {'current_year': current_year}


def user_role(request):
    return {'role': get_user_role(get_user_session_type(request))}
