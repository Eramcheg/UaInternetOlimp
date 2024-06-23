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
from shop.views_scripts import profile_views
from shop.views_scripts.adresses_views import update_address, delete_address, create_address
from shop.views_scripts.manage_banners.banners_managing import move_down, move_up, delete_banner
from shop.views_scripts.orders_control.bulk_change_statuses import change_statuses
from shop.views_scripts.orders_control.download_order import download_csv_order, download_pdf_w_img, \
    download_pdf_no_img, at_delete_order
from shop.views_scripts.orders_control.view_order import view_order, change_in_stock, upload_in_stock
from shop.views_scripts.service_views import service_pages_view, company_info_pages
from shop.views_scripts.users_control.at_uc_bulk_actions import disable_users, enable_users
from shop.views_scripts.auth_views import register, logout_view, login_view
from shop.views_scripts.catalog_views import add_to_cart_from_catalog, catalog_view, change_favorite_state
from shop.views_scripts.checkout_cart_views import sort_documents, send_email, cart_page, anonym_cart_info, \
    register_anonym_cart_info, login_anonym_cart_info, checkout_addresses
from shop.views_scripts.profile_views import update_user_account
from shop.views_scripts.shop_views import fetch_numbers, form_page
from shop.views_scripts.users_control.edit_user import edit_user
from shop.views_scripts.users_control.view_user import view_user
from django.conf.urls.i18n import i18n_patterns

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('shop/', form_page, name='shop_page'),
    path('catalog/', catalog_view, name='catalog'),
    path('cart/', cart_page, name='cart'),
    path('order/anonymous/info', anonym_cart_info, name='cart_anonymous'),
    path('checkout/addresses', checkout_addresses, name='checkout_addresses'),
    path('anonymous/cart/login', login_anonym_cart_info, name='cart_anonymous_login'),
    path('anonymous/cart/register', register_anonym_cart_info, name='cart_anonymous_register'),

    # Addresses urls
    path('profile/addresses/update_address/<str:address_id>/', update_address, name='update_address'),
    path('profile/addresses/delete_address/<str:address_id>/', delete_address, name='delete_address'),
    path('profile/addresses/create_new/', create_address, name='create_address'),

    path('profile/<str:feature_name>/', profile_views.profile, name='profile'),
    path('update_user_account/', update_user_account, name='update_user_account'),

    path('fetch-numbers/', fetch_numbers, name='fetch_numbers'),

    path('delete-document/', views.deleteProduct, name='delete_document'),
    path('update_quantity_input/', views.update_quantity_input, name='update_input'),

    path('sort_documents/', sort_documents, name='sort_documents'),
    path('send-email/', send_email, name='send_email'),

    path('add_to_cart_from_catalog/', add_to_cart_from_catalog, name='add_from_catalog'),
    path('changeFavoriteState/', change_favorite_state, name='change_favorite_state'),
    path('get_cart/', views.getCart, name='get_cart'),

    path('admin_tools/<str:feature_name>/', views.admin_tools, name='admin_tools'),
    path('at/enable_users/', enable_users, name='at_enable_users'),
    path('at/disable_users/', disable_users, name='at_disable_users'),
    path('at/delete_users/', views.delete_users, name='at_delete_users'),

    path('admin_tools/users_control/edit_user/<str:user_id>/', edit_user, name='at_edit_user'),
    path('admin_tools/users_control/view_user/<str:user_id>/', view_user, name='at_view_user'),
    path('change_statuses/', change_statuses, name='change_few_statuses'),
    path('admin_tools/orders_control/view_order/<str:order_id>/', view_order, name='at_view_order'),
    path('admin_tools/orders_control/download_csv/<str:order_id>/', download_csv_order, name='at_download_csv'),
    path('admin_tools/orders_control/download_pdf_no_img/<str:order_id>/', download_pdf_no_img, name='at_download_pdf_no_img'),
    path('admin_tools/orders_control/download_pdf_with_img/<str:order_id>/', download_pdf_w_img, name='at_download_pdf_w_img'),
    path('admin_tools/orders_control/delete_order/<str:order_id>/', at_delete_order, name='at_delete_order'),
    path('admin_tools/orders_control/edit_product_in_stock/', change_in_stock, name='change_in_stock'),
    path('admin_tools/orders_control/upload_in_stock/<str:order_id>/', upload_in_stock, name='upload_in_stock'),
    # path('finish_order/', )

    #Service urls
    path('service_pages/<str:service_page>/', service_pages_view, name='services'),
    path('our_company/<str:company_info_page>/', company_info_pages, name='company_info'),
    path('delete-banner/<int:banner_id>/', delete_banner, name='delete_banner'),
    path('move-up/<int:banner_id>/', move_up, name='move_up'),
    path('move-down/<int:banner_id>/', move_down, name='move_down'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)