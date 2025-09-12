"""
URL configuration for OnlineShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop import views
from shop.views import ArticleDetailView, news_main_view, open_news, contact_us_page, task_solutions, olimp_results, \
    final_results, fourth_step_results, materials_view
from shop.views_scripts import profile_views
from shop.views_scripts.jury_control.jury_views import handle_max_score, jurys_control, submit_criteria, \
    reject_criteria, approve_criteria, get_students, get_criteria, evaluate_task, clear_task_evaluation, \
    download_users_file, get_task_actions, get_assignments_by_tour
from shop.views_scripts.manage_articles.create_article import create_article, delete_article, move_up_article, \
    move_down_article, edit_article
from shop.views_scripts.users_control.at_uc_bulk_actions import disable_users, enable_users
from shop.views_scripts.auth_views import register, logout_view, login_view, school_registration, \
    school_registration_success, lockout_view
from shop.views_scripts.profile_views import update_user_account, download_file, upload_file
from shop.views_scripts.users_control.edit_user import edit_user
from shop.views_scripts.users_control.view_user import view_user
from django.conf.urls.i18n import i18n_patterns

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = i18n_patterns(
path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('materials/', materials_view, name='materials'),
    path('news/', news_main_view, name='news_main'),
    path('task-solutions/', task_solutions, name='tasks_solutions'),
    path('results/', olimp_results, name='olimp_results'),
    path('final-results/', final_results, name='final_results'),
    path('4-step-results/', fourth_step_results, name='4_step_results'),

    path('profile/<str:feature_name>/', profile_views.profile, name='profile'),
    path('update_user_account/', update_user_account, name='update_user_account'),
    path('download/<str:filename>/', download_file, name='download_file'),
    path('upload-file/', upload_file, name='upload_file'),

    path('admin_tools/<str:feature_name>/', views.admin_tools, name='admin_tools'),

    path('at/enable_users/', enable_users, name='at_enable_users'),
    path('at/disable_users/', disable_users, name='at_disable_users'),
    path('at/delete_users/', views.delete_users, name='at_delete_users'),

    path('admin_tools/users_control/edit_user/<str:user_id>/', edit_user, name='at_edit_user'),
    path('admin_tools/users_control/view_user/<str:user_id>/', view_user, name='at_view_user'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('create-article/', create_article, name='create_article'),
    path('edit_article/<int:article_id>/', edit_article, name='edit_article'),
    path('delete-article/<int:article_id>/', delete_article, name='delete_article'),
    path('move-up-article/<int:article_id>/', move_up_article, name='move_up_article'),
    path('move-down-article/<int:article_id>/', move_down_article, name='move_down_article'),
    path('news/<str:news_number>/', open_news, name='open_news'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('school-registration/', school_registration, name='school_registration'),
    path('school-registration-success/', school_registration_success, name='school_registration_success'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('lockout/', lockout_view, name='lockout_view'),


    path('contacts/', contact_us_page, name='contact_us'),

    # Jury urls
    path('submit_score/', handle_max_score, name='submit_max_score'),
    path('update-jurys/', jurys_control, name='update_jurys'),
    path('submit-criteria/', submit_criteria, name='submit_criteria'),
    path('approve-criteria/', approve_criteria, name='approve_criteria'),
    path('reject-criteria/', reject_criteria, name='reject_criteria'),
    # path('articles/create/', create_article, name='create_article'),

    path('api/students/', get_students, name='api_get_students'),
    path('api/assignments/', get_assignments_by_tour, name='api_get_assignments'),
    path('api/criteria/', get_criteria, name='api_get_criteria'),
    path('api/evaluate/', evaluate_task, name='api_evaluate_task'),
    path('api/get-actions/', get_task_actions, name='api_get_actions'),
    path('api/clear-evaluation/', clear_task_evaluation, name='api_clear_evaluation'),
    path('api/download-file/<str:student_id>/<str:paralel>/<int:task_id>/', download_users_file, name='api_download_file'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)