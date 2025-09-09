import json
import mimetypes
import os
import re
from collections import defaultdict
from datetime import datetime

import requests
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from firebase_admin import firestore

from shop.views import users_ref, tasks_ref, TASKS, criteria_ref, actions_ref, assignments_ref, current_tour, db, \
    current_year


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
    tasks = tasks_ref.where("year", "==", current_year).stream()

    # Словарь для хранения задач в нужном формате
    tasks_dict = {}

    for task in tasks:
        task_data = task.to_dict()
        task_id = task_data['task_id']  # Пример task_id: '9_1'
        if task_data['tour'] != current_tour:
            continue
        # Извлекаем максимальное количество баллов из данных задачи
        max_points = task_data.get('max_points', 0)  # Если max_points отсутствует, по умолчанию ставим 0
        status = task_data.get('task_status', '')  # Если max_points отсутствует, по умолчанию ставим 0
        name = task_data.get('name', '')  # Если max_points отсутствует, по умолчанию ставим 0
        clas = task_data.get('class', '')  # Если max_points отсутствует, по умолчанию ставим 0

        # Формируем ключ для словаря (например, task9_1)
        task_key = f"task{task_id}"

        # Сохраняем данные в словарь с ключами task9_1, task10_1 и т.д.
        tasks_dict[task_key] = {'max_points': max_points, 'status': status, 'name': name, 'class': clas, 'task_id': task_id, 'task_id_normal': task_id.split("_", 2)[0]}

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
    admins_jury_query = users_ref.where('role', '==', 'Admin')

    # Получаем результаты обоих запросов
    simple_jury_docs = simple_jury_query.stream()
    main_jury_docs = main_jury_query.stream()
    admins_jury_docs = admins_jury_query.stream()

    # Объединяем результаты
    all_docs = list(simple_jury_docs) + list(main_jury_docs) + list(admins_jury_docs)

    admins = []
    for doc in all_docs:
        admin_data = doc.to_dict()
        admins.append({
            'id': doc.id,  # ID документа в Firestore, для дальнейшего обновления
            'name': admin_data.get('first_name') + " " + admin_data.get('last_name'),  # Имя админа (или другое подходящее поле)
            'allowed_tasks': admin_data.get('allowed_tasks', {})  # Получаем существующие разрешения, если есть
        })
    admins.sort(key=lambda x: x['name'])
    return admins


def submit_criteria(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    data = json.loads(request.body)
    task_id = data.get('task_id')
    criteria_list = data.get('criteria', [])

    if not task_id:
        return JsonResponse({'success': False, 'error': 'Task id is required.'})

    try:
        paralel = int(task_id.split('_')[0])
        task_num = task_id.split('_')[1]
    except Exception:
        return JsonResponse({'success': False, 'error': 'Bad task_id format'})

    existing_snap = (criteria_ref
         .where('task_id', '==', task_id)
         .where('paralel', '==', paralel)
         .where('tour', '==', current_tour)
         .where('year', '==', current_year)
         .stream())

    existing_by_num = {}
    for d in existing_snap:
        doc_data = d.to_dict() or {}
        num = doc_data.get('num')
        if num is not None:
            existing_by_num[int(num)] = (d.id, doc_data)

    incoming_by_num = {}
    for c in criteria_list:
        try:
            num = int(c['num'])
        except Exception:
            continue
        payload = {
            'criterion_text': c.get('criterion_text', ''),
            'num': num,
            'paralel': paralel,
            'points': c.get('points', 0),
            'task_id': task_id,
            'tour': current_tour,
            'year': current_year,
        }
        incoming_by_num[num] = payload
    batch = db.batch()
    upserts = 0
    deletes = 0

    for num, payload in incoming_by_num.items():
        doc_id = f"task_{task_num}_{num}_class_{paralel}_tour_{current_tour}_{current_year}"
        doc_ref = criteria_ref.document(doc_id)
        existed = existing_by_num.get(num)

        if existed:
            _, old = existed
            comparable_old = {
                'criterion_text': old.get('criterion_text', ''),
                'num': int(old.get('num', num)),
                'paralel': int(old.get('paralel', paralel)),
                'points': old.get('points', 0),
                'task_id': old.get('task_id', task_id),
                'tour': old.get('tour', current_tour),
                'year': old.get('year', ""),
            }
            if comparable_old == payload:
                continue
        batch.set(doc_ref, payload, merge=True)
        upserts += 1

    to_delete_nums = set(existing_by_num.keys()) - set(incoming_by_num.keys())
    for num in to_delete_nums:
        existing_doc_id, _ = existing_by_num[num]
        batch.delete(criteria_ref.document(existing_doc_id))
        deletes += 1

    batch.commit()

    return JsonResponse({'success': True, 'upserts': upserts, 'deletes': deletes})

def approve_criteria(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')

        try:
            # Обновление статуса задачи на "approved" в коллекции tasks_ref
            paralel = task_id.split('_')[0]
            task_num = task_id.split('_')[1]
            task_id_ = f"task_{task_num}_class_{paralel}_tour_{current_tour}_{current_year}"
            task_doc = tasks_ref.document(task_id_)
            task_doc.update({'task_status': 'Approved'})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def reject_criteria(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')

        try:
            # Удаление всех критериев, связанных с переданным task_id
            # criteria_docs = criteria_ref.where('task_id', '==', task_id).stream()
            # for doc in criteria_docs:
            #     doc.reference.delete()

            # Обновление статуса задачи на "rejected" в коллекции tasks_ref
            paralel = task_id.split('_')[0]
            task_num = task_id.split('_')[1]
            task_id_ = f"task_{task_num}_class_{paralel}_tour_{current_tour}_{current_year}"
            task_doc = tasks_ref.document(task_id_)
            task_doc.update({'task_status': 'Rejected'})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def get_students_by_class(user_class):

    students_query = users_ref.where('paralel', '==', user_class).where('role', '==', 'Student')
    students = students_query.stream()

    student_list = []
    for student in students:
        student_dict = student.to_dict()
        student_dict['id'] = student_dict['userId']
        student_list.append(student_dict)
    return student_list


def get_assignments(user_class):
    assignments_query = (assignments_ref.where('paralel', '==', user_class)
                         .where('tour', '==', current_tour)
                         .where('year', '==', current_year))
    assignments = assignments_query.stream()

    grouped = defaultdict(list)

    for assignment in assignments:
        assignment_dict = assignment.to_dict()
        # сохраним id документа тоже (если нужно)
        assignment_dict['docId'] = assignment.id
        user_id = assignment_dict.get('userId')
        if user_id:
            grouped[user_id].append(assignment_dict)

    # Если нужен массив объектов [{userId: [tasks]}]
    result = [{user_id: tasks} for user_id, tasks in grouped.items()]
    return result


def get_students(request):
    class_number = request.GET.get('class', 9)  # Класс по умолчанию - 9
    students = get_students_by_class(class_number)
    return JsonResponse({'students': students})


def get_assignments_by_tour(request):
    class_number = request.GET.get('class', 9)
    assignments = get_assignments(class_number)
    return JsonResponse({'assignments': assignments})


def get_criteria(request):
    task_id = request.GET.get('task_id')

    # Ищем задачу по task_id
    tasks_query = (tasks_ref.where('task_id', '==', task_id)
                   .where('tour', '==', current_tour)
                   .where('year', '==', current_year))
    tasks = list(tasks_query.stream())

    # Проверяем, существует ли задача и имеет ли она статус Approved
    if not tasks or tasks[0].to_dict().get('task_status') != 'Approved':
        return JsonResponse({'criteria': []})  # Возвращаем пустой массив, если статус не Approved

    # Ищем критерии, соответствующие task_id
    criteria_query = (criteria_ref.where('task_id', '==', task_id)
                      .where('tour', '==', current_tour)
                      .where('year', '==', current_year))
    criteria = criteria_query.stream()

    # Формируем список критериев
    criteria_list = [criterion.to_dict() for criterion in criteria]

    return JsonResponse({'criteria': criteria_list})


def get_task_actions(request):
    task_id = request.GET.get('task_id')
    student_id = request.GET.get('student_id')

    # Ищем задачу по task_id
    actions_query = actions_ref.where('objectId', '==', student_id + "_" + task_id)
    actions = list(actions_query.stream())

    # Формируем список критериев
    actions_list = [criterion.to_dict() for criterion in actions]

    # Convert and sort actions based on 'action_time'
    for action in actions_list:
        try:
            action_time = action['action_time']
            # Check if action_time is already a datetime-like object
            if isinstance(action_time, datetime):
                parsed_time = action_time
            else:
                # Parse 'action_time' as a string
                parsed_time = datetime.fromisoformat(str(action_time).replace("Z", "+00:00"))

            # Format the parsed time
            action['formatted_action_time'] = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError) as e:
            print(f"Error parsing action_time: {e}")
            action['formatted_action_time'] = "Invalid date"

    # Sort actions from latest to earliest based on 'action_time'
    actions_list.sort(key=lambda x: x['action_time'], reverse=True)

    return JsonResponse({'actions': actions_list})


def evaluate_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data['student_id']
        paralel = data['student_class']
        task_num = data['task_id']
        student_class = data['student_class']
        points = data['points']

        # Обновление статуса задания
        doc_id = f"{student_id}_task_{task_num}_tour_{current_tour}_class_{paralel}_{current_year}"

        assignment_ref = assignments_ref.document(doc_id)
        if assignment_ref:
            assignment_ref.update({f'status': True})

            points_array = [points[str(i)] for i in range(1, len(points) + 1)]
            assignment_ref.update({f'grading': points_array})

            action_doc_id = f"{student_id}_{student_class}_{task_num}"
            action_time = datetime.utcnow()
            actions_ref.add({
                'objectId': action_doc_id,
                'action_performer': f"{request.user.username} {request.user.email}",
                'action_time': action_time,
                'action_type': "update",
                'action_value': points # Generate a random UUID for the document ID
            })

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def clear_task_evaluation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data['student_id']
        task_num = data['task_id']
        paralel = data['student_class']

        doc_id = f"{student_id}_task_{task_num}_tour_{current_tour}_class_{paralel}_{current_year}"
        # Обновление статуса задания у студента

        assignment_ref = assignments_ref.document(doc_id)
        if assignment_ref:
            assignment_ref.update({f'status': False})
            assignment_ref.update({f'grading': firestore.DELETE_FIELD})

            action_doc_id = f"{student_id}_{paralel}_{task_num}"
            action_time = datetime.utcnow()
            actions_ref.add({
                'objectId': action_doc_id,
                'action_performer': f"{request.user.username} {request.user.email}",
                'action_time': action_time,
                'action_type': "delete",  # Generate a random UUID for the document ID
            })

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def download_users_file(request, student_id, paralel, task_id):
    student_ref = assignments_ref.where('userId', '==', student_id).get()
    file_url = ""
    if student_ref:
        student_ref = student_ref[0].to_dict()
        file_url = student_ref.get(f'fileUrl')
    response = requests.get(file_url)

    if response.status_code != 200:
        return HttpResponse("Ошибка при загрузке файла", status=404)

    # Создаем правильный ответ с заголовком для скачивания
    # Извлекаем имя файла из URL
    file_name_with_random = os.path.basename(file_url.split('?')[0])

    # Удаляем последние 6 случайных символов и подчеркивание с помощью регулярного выражения
    file_name_cleaned = re.sub(r'_[a-zA-Z0-9_]*[a-zA-Z0-9]{6}$', '', file_name_with_random)

    # Получаем расширение файла из очищенного имени файла
    _, file_extension = os.path.splitext(file_name_cleaned)

    # Генерируем имя файла для скачивания, добавляя оригинальное расширение
    download_file_name = f"{student_id}_{paralel}_{task_id}{file_extension}"

    # Определяем MIME-тип на основе расширения файла
    mime_type, _ = mimetypes.guess_type(download_file_name)

    # Создаем HTTP-ответ с правильным именем файла и MIME-типом
    django_response = HttpResponse(response.content,
                                   content_type=mime_type if mime_type else 'application/octet-stream')
    django_response['Content-Disposition'] = f'attachment; filename="{download_file_name}"'

    return django_response
