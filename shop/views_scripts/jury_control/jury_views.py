from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from shop.views import get_user_category, users_ref, is_admin, update_email_in_db, currency_dict, groups_dict, \
    serialize_firestore_document, updateChatInfo, tasks_ref


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