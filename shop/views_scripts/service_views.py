import concurrent

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, users_ref, addresses_ref, update_email_in_db, \
    get_user_category
import ast
import random
from datetime import datetime
from random import randint

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

from shop.forms import UserRegisterForm, User


def service_pages_view(request, service_page):
    context = {"service_page":service_page}
    return render(request, 'service_pages/main_service_template.html', context)


def company_info_pages(request, company_info_page):
    context = {"info_page": company_info_page}
    return render(request, 'our_company_pages/main_company_info_page.html', context)
