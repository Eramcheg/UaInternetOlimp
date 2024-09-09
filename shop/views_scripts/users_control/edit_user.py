from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from shop.views import get_user_category, users_ref, is_admin, update_email_in_db, currency_dict, groups_dict, \
    serialize_firestore_document, updateChatInfo


# TODO: изменить данную функцию под новые поля юзера, не забыть про правила валидации полей из условия задания
@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    print("Edit user " + user_id)

    existing_user = users_ref.where('userId', '==', (user_id)).limit(1).stream()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_user_data = json.loads(data.get('old'))
            new_user_data = data.get('new')

            old_email = old_user_data['email']
            new_email = new_user_data['email']
            new_password = new_user_data.get('password')  # Получаем новый пароль

            print(new_user_data)

            if new_email != old_email:
                existing_user_with_new_email = users_ref.where('email', '==', new_email).limit(1).get()
                if len(existing_user_with_new_email) > 0:
                    return JsonResponse({'status': 'error', 'message': 'User with this email exists.'}, status=400)

            User = get_user_model()
            try:
                user_instance = User.objects.get(email=old_email)

                # Обновляем email, если он изменился
                if new_email != old_email:
                    user_instance.email = new_email
                    try:
                        pass
                        # update_email_in_db(old_email, new_email)  # TODO: не забыть про существование этой функции
                        # Optionally use update_email_in_db_result for further logic
                    except Exception as e:
                        # Log the exception e
                        return JsonResponse(
                            {'status': 'error', 'message': 'An error occurred while updating documents in Firestore.'},
                            status=500)

                # Обновляем пароль, если он предоставлен
                if new_password:  # This checks if the new_password string is not empty
                    try:
                        # Проверяем новый пароль перед его установкой
                        validate_password(new_password, user_instance)
                        user_instance.set_password(new_password)
                        user_instance.save()  # Don't forget to save the user object after setting the new password

                    except ValidationError as e:
                        # Возвращаем ошибку, если пароль не прошел валидацию
                        return JsonResponse({'status': 'error', 'message': list(e.messages)}, status=400)



                user_instance.save()  # Сохраняем изменения в базе данных

            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            user_enabled = False if 'enable-user' not in new_user_data else True if new_user_data[
                                                                                        'enable-user'] == "1" else False
            paralel = new_user_data['paralel']
            if (old_user_data['paralel'] != new_user_data['paralel'] or
                    old_user_data['first_name'] != new_user_data['firstname'] or
                    old_user_data['last_name'] != new_user_data['lastname']):
                updateChatInfo(old_user_data, new_user_data)
            if existing_user:
                for user in existing_user:
                    user_ref = users_ref.document(user.id)
                    user_ref.update({
                        'Enabled': user_enabled,
                        'first_name': new_user_data['firstname'],
                        'last_name': new_user_data['lastname'],
                        'third_name': new_user_data['thirdname'],
                        'email': new_user_data['email'],
                        'school': new_user_data['school'],
                        'role': new_user_data['id_group'],
                        'rights': new_user_data['id_rights'],
                        'paralel': paralel
                    })
            return JsonResponse({'status': 'success', 'message': 'Address updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    context = {
        'feature_name': "edit_user",
    }
    for user in existing_user:
        user_ref = users_ref.document(user.id)
        user_data = serialize_firestore_document(user_ref.get())
        information = json.dumps(user_data)
        # information = json.dumps(user_data)  # Now it should work without errors
        information2 = json.loads(information)
        context['user_info'] = information2
        context['user_info_dict'] = information
    print(context)
    return render(request, 'admin_tools.html', context)
