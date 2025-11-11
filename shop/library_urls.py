from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    path("", views.LibraryGridView.as_view(), name="library_grid"),
    path("<slug:slug>/", views.MaterialsListView.as_view(), name="library_detail"),
]