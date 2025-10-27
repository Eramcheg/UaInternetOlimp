from django.urls import path
from . import views

app_name = "olymps"

urlpatterns = [
    path("", views.GroupGridView.as_view(), name="group_grid"),
    path("<slug:slug>/", views.OlympiadListView.as_view(), name="group_detail"),
]