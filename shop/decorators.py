from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from functools import wraps

from django.urls import reverse


def login_required_or_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.session_key:
            return f(request, *args, **kwargs)
        else:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    return wrapper

def logout_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('checkout_addresses'))  # Redirect to a named URL 'home'
        else:
            return function(request, *args, **kwargs)
    return wrap