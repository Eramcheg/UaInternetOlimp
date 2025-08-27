import json
import os
import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import storage, firestore

from shop.views import db, serialize_firestore_document, users_ref, get_user_info, \
    updateChatInfo, TASKS, \
    criteria_ref, current_tour, assignments_ref
from shop.views_scripts.jury_control.jury_views import get_all_tasks, get_jury_admins, get_students_by_class


@login_required
def profile(request, feature_name):
    # if feature_name == "upload":
    #     feature_name = "account"
    email = request.user.email
    info = get_user_info(email) or {}

    jurys = get_jury_admins()
    saved_criteria = {}
    for task in info['allowed_tasks'] if "allowed_tasks" in info else "":
        task = task + f"_{current_tour}"
        task_id = task
        criteria_docs = criteria_ref.where('task_id', '==', task_id).stream()
        criteria_list = []
        for doc in criteria_docs:
            data = doc.to_dict()

            criteria_list.append({'criterion_text': data['criterion_text'], 'points': data['points'], 'id': doc.id})
        saved_criteria[task] = criteria_list

    context = dict()
    context['feature_name'] = feature_name

    if feature_name == "dashboard":
        pass
    elif feature_name == "tasks":
        context['user_class'] = info.get('paralel', 9)
    elif feature_name == "account":
        context['user_info'] = info
    elif feature_name == "upload":
        docs = assignments_ref.where("userId", "==", info['userId']).where('tour', '==', current_tour).stream()
        for d in docs:
            data = d.to_dict() or {}
            task_key = data.get("taskKey")  # например: "task_1"
            file_name = data.get("name")  # у тебя же это поле хранит имя файла
            if task_key and file_name:
                context[task_key] = file_name
            else:
                # если задания нет — оставляем пустым
                context[data.get("taskKey", "unknown")] = None
    elif feature_name == "solutions":
        pass
    elif feature_name == "points":
        context['tasks'] = get_all_tasks()
    elif feature_name == "jury_control":
        context['tasks_numbers'] = [y for y in
                                    sorted(TASKS, key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1])))]
        context['jurys'] = jurys
    elif feature_name == "criteria_create":
        context['jury_tasks'] = [inf + f"_{current_tour}" for inf in info.get('allowed_tasks', "")]
        context['tasks'] = get_all_tasks()
        context['saved_criteria'] = saved_criteria

    elif feature_name == "criteria_approve":
        context['tasks_numbers'] = [y + f"_{current_tour}" for y in
                                    sorted(TASKS, key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1])))]
        context['jury_tasks'] = [inf + f"_{current_tour}" for inf in info.get('allowed_tasks', "")]
        context['tasks'] = get_all_tasks()
        context['saved_criteria'] = saved_criteria
    elif feature_name == "verification":
        context['jury_tasks'] = [inf + f"_{current_tour}" for inf in info.get('allowed_tasks', "")]

    elif feature_name == "chat":
        context['user_class'] = info.get('paralel', 9)

    else:
        pass

    context['role'] = info['role']
    context['userId'] = info['userId']
    context['username'] = info['first_name'] + " " + info["last_name"]
    context['rights'] = info['rights'] if "rights" in info else ""

    return render(request, 'profile.html', context=context)


def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d") if date_obj else None


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
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    file = request.FILES.get('file')
    box_id = request.POST.get('box_id')
    user_email = request.user.email  # Assuming user is authenticated

    if not file or not box_id:
        return JsonResponse({'success': False, 'error': 'No file or box_id provided'}, status=400)

    user_ref = users_ref.where('email', '==', user_email).limit(1).get()
    if not user_ref:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    user_doc = user_ref[0].to_dict()
    user_id = user_doc.get('userId')
    paralel = user_doc.get('paralel')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'userId missing in user profile'}, status=400)

    code_file = generate_random_string()
    file_path = os.path.join(
        'users_files',
        f"{user_email}_Task_{box_id}_{file.name}_{current_tour}_tour_{code_file}"
    )
    blob = upload_to_firebase(file, file_path)
    file_url = blob.public_url

    # Update user's document in Firestore
    assignment_doc_id = f"{user_id}_{box_id}_{paralel}_tour_{current_tour}"
    assignment_payload = {
        "createdAt": firestore.SERVER_TIMESTAMP,
        "fileUrl": file_url,
        "grading": [],
        "name": file.name,
        "paralel": paralel,
        "taskKey": f"task_{box_id.replace('box', '')}",  # например "task_1"
        "tour": current_tour,
        "userId": user_id,
    }
    assignments_ref.document(assignment_doc_id).set(assignment_payload, merge=True)

    return JsonResponse({'success': True, 'file_url': file_url})
