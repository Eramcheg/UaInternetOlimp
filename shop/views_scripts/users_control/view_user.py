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
from shop.views import addresses_ref, cart_ref, get_user_category, serialize_firestore_document, users_ref, is_admin


@login_required
@user_passes_test(is_admin)
def view_user(request, user_id):
    print("View user " + user_id)

    existing_user = users_ref.where('userId', '==', int(user_id)).limit(1).stream()
    email = request.user.email
    category, currency = get_user_category(email)
    currency = '€' if currency == 'Euro' else '$'
    context = {
        'feature_name': "view_user",
        'currency':currency,
        'cart':[],
        'orders':[],
        'addresses': [],
    }

    for user in existing_user:
        user_ref = users_ref.document(user.id)
        user_data = serialize_firestore_document(user_ref.get())

        # Assuming user_data contains 'email', adjust if necessary
        user_email = user_data.get('email', '')

        category, currency = get_user_category(user_email)
        context['user_currency'] = "€" if currency == "Euro" else "$"

        # Fetch orders related to the user
        from shop.views_scripts.profile_views import get_orders_for_user
        orders = get_orders_for_user(user_email)
        currencies_dict = {}
        for order in orders:
            currencies_dict[order['order_id'] if 'order_id' in order.keys() else order['order-id']] = "€" if (order[
                                                                                                                  'currency'] if 'currency' in order else "Euro") == "Euro" else "$"

        context['orders'] = orders
        context['currencies'] = currencies_dict

        # Fetch addresses related to the user
        addresses_query = addresses_ref.where('email', '==', user_email).stream()
        context['addresses'] = [address.to_dict() for address in addresses_query]

        # Fetch cart items related to the user
        # Assuming cart collection documents contain user email, adjust if your schema is different
        cart_query = cart_ref.where('emailOwner', '==', user_email).stream()
        cart_items = []
        for item in cart_query:
            item_dict = item.to_dict()
            # Assuming 'price' and 'quantity' are fields in your item documents
            # Calculate the total price for each item (price * quantity)
            total_price = round(item_dict.get('price', 0) * item_dict.get('quantity', 0),2)
            # Add the total price to the item dictionary
            item_dict['total_price'] = total_price
            cart_items.append(item_dict)
        context['cart'] = cart_items

        # User information - to_dict() can be used directly
        context['user_info'] = user_data

        # Convert user_data to JSON string if you need to pass it as a string in the context
        context['user_info_dict'] = json.dumps(user_data)
        print(context['cart'])
    return render(request, 'admin_tools.html', context)