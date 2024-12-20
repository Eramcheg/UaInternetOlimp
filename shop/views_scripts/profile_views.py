import concurrent
import string

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, users_ref, addresses_ref, update_email_in_db, \
    get_user_category, get_user_info, get_vocabulary_product_card, chats_ref, messages_ref, updateChatInfo, TASKS, \
    criteria_ref
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
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User
from firebase_admin import storage

from shop.views_scripts.jury_control.jury_views import get_all_tasks, get_jury_admins, get_students_by_class


@login_required
def profile(request, feature_name):
    email = request.user.email
    if feature_name == "upload":
        feature_name = "account"
    orders = get_orders_for_user(email)
    order_details = get_order_details(orders)
    email = request.user.email
    category, currency = 0, 1
    info = get_user_info(email) or {}
    show_quantities = info['show_quantities'] if 'show_quantities' in info else False

    jurys = get_jury_admins()

    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    context = build_context(feature_name, email, orders, order_details)

    saved_criteria = {}
    for task in info['allowed_tasks'] if "allowed_tasks" in info else "":
        criteria_docs = criteria_ref.where('task_id', '==', task+"_2_tour").stream()
        criteria_list = []
        for doc in criteria_docs:
            data = doc.to_dict()

            criteria_list.append({'criterion_text': data['criterion_text'], 'points': data['points'], 'id': doc.id})
        saved_criteria[task] = criteria_list
    students = get_students_by_class(9)  # Создадим эту функцию позже


    context['students'] = students
    context['default_class'] = 9  # По умолчанию показываем класс 9

    context['saved_criteria'] = saved_criteria
    context['jurys'] = jurys
    context['tasks_numbers'] = sorted(TASKS, key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1])))
    context['tasks'] = get_all_tasks()

    context['jury_tasks'] = info['allowed_tasks'] if "allowed_tasks" in info else ""
    context['currency'] = currency
    context['role'] = info['role']
    context['userId'] = info['userId']
    context['user_class'] = info['paralel'] if "paralel" in info else ""
    context['username'] = info['first_name'] + " " + info["last_name"]
    context['show_quantities'] = show_quantities
    context['task_1'] = info['task_1_name'] if "task_1_name" in info else ""
    context['task_2'] = info['task_2_name'] if "task_2_name" in info else ""
    context['task_3'] = info['task_3_name'] if "task_3_name" in info else ""
    context['task_4'] = info['task_4_name'] if "task_4_name" in info else ""
    context['task_5'] = info['task_5_name'] if "task_5_name" in info else ""
    context['task_1_2_tour'] = info['task_1_2_tour_name'] if "task_1_2_tour_name" in info else ""
    context['task_2_2_tour'] = info['task_2_2_tour_name'] if "task_2_2_tour_name" in info else ""
    context['task_3_2_tour'] = info['task_3_2_tour_name'] if "task_3_2_tour_name" in info else ""
    context['task_4_2_tour'] = info['task_4_2_tour_name'] if "task_4_2_tour_name" in info else ""
    context['task_5_2_tour'] = info['task_5_2_tour_name'] if "task_5_2_tour_name" in info else ""
    context['rights'] = info['rights'] if "rights" in info else ""

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
    currencies_dict = {}
    for order in orders:
        currencies_dict[order['order_id'] if 'order_id' in order.keys() else order['order-id']] = "€" if (order[
                                                                                                              'currency'] if 'currency' in order else "Euro") == "Euro" else "$"

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

            if new_data['email'] != old_email or new_data['login'] != old_data['login']:
                if (new_email != old_email):
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

            user_image = request.FILES.get('profile_picture')
            photo_url = ""
            if user_image:
                file_path = os.path.join('profile_pics', user_image.name)
                blob = upload_to_firebase(user_image, file_path)

                # Now you can save `blob.public_url` to your user profile model
                print(blob.public_url)
                photo_url = blob.public_url

            user_instance.save()
            if (old_data['paralel'] != new_data['paralel'] or
                    old_data['first_name'] != new_data['firstname'] or
                    old_data['last_name'] != new_data['lastname']):
                updateChatInfo(old_data, new_data)

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


def generate_random_string(length=6):
    # Объединяем цифры и буквы в один набор символов
    characters = string.ascii_lowercase + string.digits
    # Генерируем случайную строку
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'tasks', filename)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        raise Http404("File not found")


def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        box_id = request.POST.get('box_id')
        user_email = request.user.email  # Assuming user is authenticated

        if not file:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)

        # Generate file path in Firebase Storage
        file_path = f'{user_email}/{box_id}/{file.name}'

        code_file = generate_random_string()

        # Upload to Firebase Storage
        file_path = os.path.join('users_files', f"{user_email}_Task_{box_id}_{file.name}_2_tour_{code_file}")
        blob = upload_to_firebase(file, file_path)
        # Generate the file URL
        file_url = blob.public_url

        # Update user's document in Firestore
        users_ref = db.collection('users')
        user_ref = users_ref.where('email', '==', user_email).limit(1).get()

        if user_ref:
            user_doc = user_ref[0]
            field_name = f'task_{box_id[-1]}_2_tour'  # file_1, file_2, ...
            name_field_name = f'task_{box_id[-1]}_2_tour_name'  # file_1, file_2, ...
            user_doc.reference.update({field_name: file_url})
            user_doc.reference.update({name_field_name: file.name})

        return JsonResponse({'success': True, 'file_url': file_url})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
