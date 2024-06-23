import ast
import random
from datetime import datetime
from random import randint
import geoip2.database

import concurrent.futures
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
import firebase_admin
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User, BannerForm
from django.utils.translation import gettext as _

from shop.models import Banner
from shop.views import is_admin
from django.core.files.storage import default_storage

@login_required
@user_passes_test(is_admin)
def delete_banner(request, banner_id):
    # Получаем объект баннера, чтобы иметь доступ к связанному файлу изображения
    banner = Banner.objects.filter(id=banner_id).first()
    if banner:
        # Удаление файла изображения
        if banner.image:
            # Удаление файла, если он существует
            image_path = banner.image.path
            if default_storage.exists(image_path):
                default_storage.delete(image_path)
        # Удаление объекта баннера
        banner.delete()
        # Перенумерация приоритетов оставшихся баннеров
        banners = Banner.objects.all().order_by('priority')
        for index, remaining_banner in enumerate(banners):
            remaining_banner.priority = index
            remaining_banner.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Banner not found'})

@login_required
@user_passes_test(is_admin)
def move_up(request, banner_id):
    banner = Banner.objects.get(id=banner_id)
    previous_banner = Banner.objects.filter(priority__lt=banner.priority).order_by('-priority').first()
    if previous_banner:
        banner.priority, previous_banner.priority = previous_banner.priority, banner.priority
        banner.save()
        previous_banner.save()
    return JsonResponse({'status': 'ok'})

@login_required
@user_passes_test(is_admin)
def move_down(request, banner_id):
    banner = Banner.objects.get(id=banner_id)
    next_banner = Banner.objects.filter(priority__gt=banner.priority).order_by('priority').first()
    if next_banner:
        banner.priority, next_banner.priority = next_banner.priority, banner.priority
        banner.save()
        next_banner.save()
    return JsonResponse({'status': 'ok'})