from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from shop.views import get_user_category, users_ref, is_admin, update_email_in_db, currency_dict, groups_dict, \
    serialize_firestore_document, updateChatInfo, tasks_ref, TASKS, criteria_ref


def handle_max_score(request):
    if request.method == 'POST':
        # Получаем значения из формы
        task_id = request.POST.get('task_id')
        max_score = request.POST.get('max_score')

        # Проверяем, что необходимые данные присутствуют
        if not task_id or not max_score:
            return JsonResponse({'message': 'Некорректные данные. Пожалуйста, введите валидный идентификатор задачи и баллы.'}, status=400)

        try:
            # Преобразуем max_score в целое число, если необходимо
            max_score = int(max_score)

            # Обновляем задачу в Firebase
            task_ref = tasks_ref.document(task_id)
            task_ref.update({'max_points': max_score})

            # Возвращаем успешный ответ
            return JsonResponse({'message': f'Задача {task_id} обновлена. Новые бали: {max_score}'}, status=200)
        except ValueError:
            # Обработка ошибки, если max_score не является числом
            return JsonResponse({'message': 'Некорректное значение баллов. Введите числовое значение.'}, status=400)
        except Exception as e:
            # Общий обработчик ошибок
            return JsonResponse({'message': f'Ошибка при обновлении задачи: {str(e)}'}, status=500)

    # Если запрос не является POST
    return JsonResponse({'message': 'Неправильный запрос.'}, status=405)


def get_all_tasks():
    # Получаем все документы из коллекции 'tasks'
    tasks = tasks_ref.stream()

    # Словарь для хранения задач в нужном формате
    tasks_dict = {}

    for task in tasks:
        task_data = task.to_dict()
        task_id = task.id  # Пример task_id: '9_1'

        # Извлекаем максимальное количество баллов из данных задачи
        max_points = task_data.get('max_points', 0)  # Если max_points отсутствует, по умолчанию ставим 0

        # Формируем ключ для словаря (например, task9_1)
        task_key = f"task{task_id}"

        # Сохраняем данные в словарь с ключами task9_1, task10_1 и т.д.
        tasks_dict[task_key] = {'max_points': max_points}

    return tasks_dict


def jurys_control(request):
    admins = get_jury_admins()
    tasks = TASKS
    if request.method == 'POST':
        # Получаем данные с формы
        data = request.POST

        # Обрабатываем каждую галочку для каждого админа
        for admin in admins:
            admin_id = admin['id']
            allowed_tasks = []
            for task in tasks:
                if data.get(f"{admin_id}_{task}") == 'on':
                    allowed_tasks.append(task)

            # Сохраняем в Firebase
            users_ref.document(admin_id).update({
                'allowed_tasks': allowed_tasks
            })
        return redirect('profile', feature_name='jury_control')  # Перенаправляем после успешного сохранения

    return render(request, 'superadmin.html', {'admins': admins, 'tasks': tasks})

def get_jury_admins():
    simple_jury_query = users_ref.where('role', '==', 'Simple_Jury')
    main_jury_query = users_ref.where('role', '==', 'Main_Jury')

    # Получаем результаты обоих запросов
    simple_jury_docs = simple_jury_query.stream()
    main_jury_docs = main_jury_query.stream()

    # Объединяем результаты
    all_docs = list(simple_jury_docs) + list(main_jury_docs)

    admins = []
    for doc in all_docs:
        admin_data = doc.to_dict()
        admins.append({
            'id': doc.id,  # ID документа в Firestore, для дальнейшего обновления
            'name': admin_data.get('first_name') + " " + admin_data.get('last_name'),  # Имя админа (или другое подходящее поле)
            'allowed_tasks': admin_data.get('allowed_tasks', {})  # Получаем существующие разрешения, если есть
        })
    return admins


def submit_criteria(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        criteria_list = data.get('criteria', [])

        try:
            # Сохранение критериев в базе данных Firebase
            for criterion in criteria_list:
                criteria_ref.document(criterion['id']).set({
                    'criterion_text': criterion['criterion_text'],
                    'points': criterion['points'],
                    'task_id': task_id,
                })

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})