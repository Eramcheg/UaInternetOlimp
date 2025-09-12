from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

def advanced_redirect(request, destination, **kwargs):
    try:
        url = reverse(destination, kwargs=kwargs)  # если это имя
    except NoReverseMatch:
        url = destination  # значит это уже путь (/gb/...)
    query = request.META.get("QUERY_STRING")
    if query:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{query}"
    return redirect(url)
