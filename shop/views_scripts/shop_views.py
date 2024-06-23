import concurrent

from django.contrib.auth.decorators import login_required

from shop.decorators import login_required_or_session
from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, users_ref, \
    get_user_category, get_user_info, get_user_session_type, get_user_prices
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


@login_required_or_session
def form_page(request):
    documents = []
    search_term = ''
    email = get_user_session_type(request)
    if request.method == 'POST':
        search_term = request.POST.get('number').upper()

        documents = itemsRef.where('name', '==', search_term).stream()

    cart = get_cart(email)
    quantity = 1
    inside = False
    for prod in cart:
        if search_term == prod['name']:
            inside = True
            quantity = prod['quantity']
            break

    category, currency = get_user_prices(request, email)
    info = get_user_info(email) or {}
    sale = round((0 if "sale" not in info else info['sale'])/100, 2) or 0

    products = [{key: value for key, value in doc.to_dict().items() if key != 'Visible'} for doc in documents]


    # print(products)
    for obj in products:
        if category == "VK3":
            del obj['price']
            obj['price'] = obj['priceVK3']
        if category == "GH":
            del obj['price']
            obj['price'] = obj['priceGH']
        if category == "USD_GH":
            del obj['price']
            obj['price'] = obj['priceUSD_GH']
        if category == "Default_USD":
            del obj['price']
            obj['price'] = round(obj['priceUSD'] * (1-sale), 1)
        else:
            del obj['price']
            obj['price'] = round(obj['priceVK4'] * (1-sale), 1)

    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    context = {
        'documents': products,
        'search_term': search_term,
        'inside': inside,
        'quantity': quantity,
        'is_authenticated': 'False',
        'in_cart': 'False',
        'cart': cart,
        'currency': currency
    }

    return render(request, 'shop_page.html', context)

def fetch_numbers(request):
    search_term = request.GET.get('term', '').lower()
    numbers = []

    if search_term != '':
        # Using Firestore query to filter documents
        name_query = itemsRef.where('name', '>=', search_term).where('name', '<=', search_term + '\uf8ff').stream()

        # Filter the results in Python for the 'quantity' field
        numbers = [
            doc.to_dict().get('name', '') for doc in name_query
            if search_term in doc.to_dict().get('name', '').lower() and
               doc.to_dict().get('quantity', 0) > 0 and
               doc.to_dict().get('Visible', True)  # Assumes default is True if 'Visible' is not present
        ]

    return JsonResponse(numbers, safe=False)

