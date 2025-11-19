from django.urls import path
from . import admin_views as views

app_name = "olymps_admin"

urlpatterns = [
    path("groups/", views.group_list, name="group_list"),
    path("groups/new/", views.group_edit, name="group_new"),
    path("groups/<int:pk>/edit/", views.group_edit, name="group_edit"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),

    path("groups/<int:group_id>/olymps/", views.olymp_list, name="olymp_list"),
    path("groups/<int:group_id>/olymps/new/", views.olymp_edit, name="olymp_new"),
    path("groups/<int:group_id>/olymps/<int:pk>/edit/", views.olymp_edit, name="olymp_edit"),
    path("groups/<int:group_id>/olymps/<int:pk>/delete/", views.olymp_delete, name="olymp_delete"),

    path("libraries/", views.library_list, name="library_list"),
    path("libraries/<int:library_id>/materials/", views.materials_list, name="material_list"),
    path("libraries/<int:library_id>/materials/new/", views.materials_edit, name="material_new"),
    path("libraries/<int:library_id>/materials/<int:pk>/edit/", views.materials_edit, name="material_edit"),
    path("libraries/<int:library_id>/materials/<int:pk>/delete/", views.materials_delete, name="material_delete"),

    path("links/new/", views.links_edit, name="links_new"),
    path("links/<int:pk>/edit/", views.links_edit, name="links_edit"),
    path("links/<int:pk>/delete/", views.links_delete, name="links_delete"),
]
