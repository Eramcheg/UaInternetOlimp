from django.urls import reverse

from shop.views import current_tour


def get_current_tour(request):
    return {'current_tour': current_tour}
