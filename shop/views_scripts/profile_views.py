import concurrent

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, users_ref, addresses_ref, update_email_in_db, \
    get_user_category, get_user_info, get_vocabulary_product_card, get_user_prices
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
from firebase_admin import storage
@login_required
def profile(request, feature_name):
    email = request.user.email
    orders = get_orders_for_user(email)
    order_details = get_order_details(orders)
    email = request.user.email
    category, currency = get_user_prices(request,email)
    info = get_user_info(email) or {}
    show_quantities = info['show_quantities'] if 'show_quantities' in info else False
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    context = build_context(feature_name, email, orders, order_details)
    context['currency'] = currency
    context['show_quantities'] = show_quantities
    return render(request, 'profile.html', context=context)

def get_orders_for_user(email):
    orders = []
    docs_orders = orders_ref.where('email', '==', email).stream()

    for doc in docs_orders:
        order_info = doc.to_dict()
        order_id = order_info.get('order_id') or order_info.get('order-id')
        formatted_date = format_date(order_info.get('date'))
        orders.append({
            'Status': order_info.get('Status'),
            'date': formatted_date,
            'email': email,
            'list': order_info.get('list'),
            'order_id': order_id,
            'sum': order_info.get('price')
        })
    return orders

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d") if date_obj else None

def get_order_details(orders):
    order_details = {order['order_id']: [] for order in orders}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_order = schedule_order_detail_fetching(executor, orders, order_details)
        for future in concurrent.futures.as_completed(future_to_order):
            order_id = future_to_order[future]
            order_doc_data = future.result()
            if order_doc_data:
                order_details[order_id].append(order_doc_data)

    return order_details

def schedule_order_detail_fetching(executor, orders, order_details):
    future_to_order = {}
    for order in orders:
        for order_doc_ref in order['list']:
            order_doc_path = order_doc_ref if type(order_doc_ref) is str else order_doc_ref.path
            future = executor.submit(fetch_order_detail, order_doc_path)
            future_to_order[future] = order['order_id']
    return future_to_order

def fetch_order_detail(order_doc_path):
    path_parts = order_doc_path.split('/')
    if len(path_parts) == 2:
        collection_name, document_id = path_parts
        order_doc_ref = db.collection(collection_name).document(document_id)
        order_doc = order_doc_ref.get()
        if order_doc.exists:
            return order_doc.to_dict()
    return None

def build_context(feature_name, email, orders, order_details):
    currencies_dict ={}
    for order in orders:
        currencies_dict[order['order_id'] if 'order_id' in order.keys() else order['order-id']] = "€" if (order['currency'] if 'currency' in order else "Euro")=="Euro" else "$"

    context = {
        'currencies': currencies_dict,
        'orders': orders,
        'products': order_details,
        'feature_name': feature_name,
        'vocabulary': get_vocabulary_product_card()
    }

    if feature_name == "account":
        context['user_info'], context['user_info_dict'] = get_user_info_dicts(email)

    if feature_name == "addresses":
        addresses, addresses_dict = get_user_addresses(email)
        context['my_addresses'] = addresses
        context['addresses_dict'] = addresses_dict

    return context

def get_user_info_dicts(email):
    existing_users = users_ref.where('email', '==', email).limit(1).get()
    if existing_users:
        for user in existing_users:
            user_ref = users_ref.document(user.id)
            user_data = serialize_firestore_document(user_ref.get())
            information = json.dumps(user_data)
            information2 = json.loads(information)
            return information2, information
    return None, None

def get_user_addresses(email):
    addresses = []
    existing_addresses = addresses_ref.where('email', '==', email).get()
    if existing_addresses:
        for address in existing_addresses:
            address_doc = addresses_ref.document(address.id).get().to_dict()
            addresses.append(address_doc)
    addresses_dict = json.dumps(addresses)
    return addresses, addresses_dict

def upload_to_firebase(file_stream, file_path):
    # Get the bucket
    bucket = storage.bucket('uainternetolimp-41dd1.appspot.com')
    blob = bucket.blob(file_path)
    blob.upload_from_file(file_stream)
    blob.make_public()  # If you want the file to be publicly accessible
    return blob
@csrf_exempt
@login_required
def update_user_account(request):
    if request.method == 'POST':
        try:
            # data = json.loads(request.body)
            old_data = json.loads(request.POST.get('old'))
            new_data = json.loads(request.POST.get('new'))

            old_email = old_data['email']
            new_email = new_data['email']

            user_image = request.FILES.get('profile_picture')
            photo_url = ""
            if user_image:
                file_path = os.path.join('profile_pics', user_image.name)
                blob = upload_to_firebase(user_image, file_path)

                # Now you can save `blob.public_url` to your user profile model
                print(blob.public_url)
                photo_url = blob.public_url


            # Check for existing user by email
            existing_users = users_ref.where('email', '==', old_email).limit(1).get()
            if new_data['firstname'] != old_data['first_name'] or new_data['lastname'] != old_data['last_name']:
                User = get_user_model()
                try:
                    user_instance = User.objects.get(email=old_email)
                    user_instance.first_name = new_data['firstname']
                    user_instance.last_name = new_data['lastname']
                    user_instance.save()
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            if new_data['email'] != old_email or new_data['login']!=old_data['login']:
                if(new_email!= old_email):
                    existing_user_with_new_email = users_ref.where('email', '==', new_email).limit(1).get()
                    if len(existing_user_with_new_email) > 0:
                        return JsonResponse({'status': 'error', 'message': 'User with this email exists.'}, status=400)
                User = get_user_model()
                try:
                    user_instance = User.objects.get(email=old_email)
                    if new_email != old_email:
                        user_instance.email = new_email  # Update the email
                    if new_data['login'] != old_data['login']:
                        if User.objects.filter(username=new_data['login']).exists():
                            return JsonResponse({'status': 'error', 'message': 'User with this email exists.'},
                                                status=400)
                        user_instance.username = new_data['login']  # Update the email

                    user_instance.save()
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

                try:
                    # update_email_in_db(old_email, new_email) # TODO: не забыть что тут будет обновление емейла во всех бд
                    # Optionally use update_email_in_db_result for further logic
                    pass
                except Exception as e:
                    # Log the exception e
                    return JsonResponse(
                        {'status': 'error', 'message': 'An error occurred while updating documents in Firestore.'},
                        status=500)
            else:
                User = get_user_model()
                try:
                    # Retrieve the user instance
                    user_instance = User.objects.get(email=old_email)
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            password = new_data['password']
            second_password = new_data.get('new_password', '')
            # Check if the provided password matches the user's password
            if not user_instance.check_password(password) or not user_instance.check_password(second_password):
                return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)

            # new_password = new_data.get('new_password', '')
            # if new_password:  # This checks if the new_password string is not empty
            #     user_instance.set_password(new_password)
            #     user_instance.save()  # Don't forget to save the user object after setting the new password
            #     update_session_auth_hash(request, user_instance)

            user_instance.save()

            for user in existing_users:
                user_ref = users_ref.document(user.id)
                user_ref.update({
                    'first_name': new_data['firstname'],
                    'last_name': new_data['lastname'],
                    'third_name': new_data['thirdname'],
                    'email': new_data['email'],
                    'login': new_data['login'],
                    'phone': new_data['phone_number'],
                    'school': new_data['school'],
                    'paralel': new_data['paralel'],
                    'photo_url': photo_url
                })
                return JsonResponse({'status': 'success', 'message': 'User updated successfully.'})

            return JsonResponse({'status': 'success', 'message': 'User account updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
