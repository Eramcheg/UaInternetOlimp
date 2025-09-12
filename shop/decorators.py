from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse, HttpResponse
from functools import wraps

from django.urls import reverse
from django_ratelimit.decorators import ratelimit

from shop.utils import advanced_redirect


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


def not_logged_in(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return advanced_redirect(request, 'home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ratelimit_with_logging(key, rate, block=False, **kwargs):
    def decorator(fn):
        @ratelimit(key=key, rate=rate, block=False, **kwargs)
        def wrapper(request, *args, **inner_kwargs):
            if getattr(request, 'limited', False):
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Перевищено ліміт спроб для IP: %s", request.META.get('REMOTE_ADDR'))
                # We return code 429 - Too Many Requests
                return HttpResponse("Забагато спроб.", status=429)
            return fn(request, *args, **inner_kwargs)
        return wrapper
    return decorator
