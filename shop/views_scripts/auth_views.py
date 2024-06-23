import concurrent

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    is_admin, users_ref, metadata_ref, get_user_prices
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


def get_new_user_id():
    @firestore.transactional
    def increment_user_id(transaction, user_counter_ref):
        snapshot = user_counter_ref.get(transaction=transaction)
        last_user_id = snapshot.get('lastUserId') if snapshot.exists else 3000
        new_user_id = last_user_id + 1
        transaction.update(user_counter_ref, {'lastUserId': new_user_id})
        return new_user_id

    user_counter_ref = metadata_ref.document('userCounter')
    transaction = db.transaction()
    new_user_id = increment_user_id(transaction, user_counter_ref)
    return new_user_id


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data.get('email')

            existing_user = users_ref.where('email', '==', email).limit(1).get()

            if list(existing_user):  # Convert to list to check if it's non-empty
                print('Error: User with this Email already exists.')
                form.add_error('email', 'User with this Email already exists.')
                return render(request, 'registration/register.html', {'form': form})
            else:

                user_id = get_new_user_id()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                birthdate = form.cleaned_data.get('birthdate')
                social_title = "Mr" if form.cleaned_data.get('social_title') == "1" else "Mrs"
                offers = form.cleaned_data.get('offers')
                newsletter = form.cleaned_data.get('receive_newsletter')
                category, currency = get_user_prices(request, email)
                new_user = {
                    'Enabled': 'True',
                    "display_name": "undefined",
                    'social_title': social_title,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'birthday': birthdate,
                    'country': "",
                    "agent_number": "",
                    'price_category': 'Default',
                    'currency': currency,
                    'receive_offers': offers,
                    'receive_newsletter': newsletter,
                    'registrationDate': current_time,
                    'userId': user_id,
                    'sale': 0,
                    'show_quantities': False

                }
                users_ref.add(new_user)

                username = email
                unique_suffix = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{unique_suffix}"
                    unique_suffix += 1
                user = form.save(commit=False)
                user.username = username  # Set the unique username
                user.save()  # Now save the user to the database

                password = form.cleaned_data.get('password1')
                form.save()
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('home')
    else:
        form = UserRegisterForm()

    print(form.errors)
    return render(request, 'registration/register.html', {'form': form, 'errors': form.errors})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                email = form.cleaned_data.get('email') or user.email

                # Query Firebase Firestore to check the user's Enabled status
                firebase_user_doc = users_ref.where('email', '==', email).limit(1).get()
                if firebase_user_doc and firebase_user_doc[0].to_dict().get('Enabled', True) == False:
                    # Redirect to home with an error message
                    messages.error(request, "Your account was disabled")
                    form.add_error(None, "Your account was disabled")
                    return render(request, 'registration/login.html', {'form': form})
                else:
                    # Proceed to log the user in
                    login(request, user)
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')