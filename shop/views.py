import concurrent.futures
import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from google.cloud.firestore_v1 import DocumentReference

from shop.forms import User, ArticleForm
from shop.models import Article

db = settings.FIRESTORE_CLIENT

assignments_ref = db.collection('assignments')
chats_ref = db.collection('chats')
criteria_ref = db.collection('criteria')
actions_ref = db.collection('jury_actions')
messages_ref = db.collection('messages')
school_registrations_ref = db.collection('school_registrations')
tasks_ref = db.collection('tasks')
users_ref = db.collection('users')

current_tour = 1

TASKS = [
    '9_1', '9_2', '9_3', '9_4', '9_5',
    '10_1', '10_2', '10_3', '10_4', '10_5',
    '11_1', '11_2', '11_3', '11_4', '11_5'
]

news_info = ["Олімпіада 2022", "Олімпіада 2023"]


def get_user_session_type(request):
    if request.user.is_authenticated:
        return request.user.email
    else:
        return request.session.session_key


def home_page(request):
    context = {
    }
    all_users = User.objects.all()
    articles = Article.objects.all().order_by('priority')
    context['news_info'] = news_info
    context['articles'] = articles
    for user in all_users:
        print(user)
    test_text = _("Welcome to my site.")
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    context['hello'] = test_text
    return render(request, 'home.html', context)


def news_main_view(request):
    articles = Article.objects.all()

    context = {
        'articles': articles
    }
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    context['news_info'] = news_info
    return render(request, 'uaolimpiad/mainPages/news.html', context)

def task_solutions(request):

    context = {

    }
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    return render(request, 'uaolimpiad/mainPages/jurysSolutions.html', context)


def olimp_results(request):

    context = {

    }
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    return render(request, 'uaolimpiad/mainPages/olimp_results.html', context)


def final_results(request):

    context = {

    }
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    return render(request, 'uaolimpiad/mainPages/final_results.html', context)


def fourth_step_results(request):

    context = {

    }
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    return render(request, 'uaolimpiad/mainPages/4_step_results.html', context)


def get_user_category(email):
    pass


def get_user_role(email):
    user = users_ref.where('email', '==', email).limit(1).get()
    if user:
        for user_info in user:
            user_dict = user_info.to_dict()
            return user_dict['role']
    else:
        return "Default", "Euro"


def get_user_info(email):
    user = users_ref.where('email', '==', email).limit(1).get()
    for user_info in user:
        user_dict = user_info.to_dict()
        return user_dict
    return {}


def update_email_in_db(old_email, new_email):
    # Define a mapping of collections to their respective email fields
    collection_email_fields = {
        # 'Cart': 'emailOwner',
        # 'Favourites': 'email',
        # 'Order': 'emailOwner',
        # 'Orders': 'email',
        # 'Addresses': 'email',
    }

    # Loop through the mapping
    for collection_name, email_field in collection_email_fields.items():
        try:
            # Reference the collection
            collection_ref = db.collection(collection_name)
            # Query for documents with the old email
            docs_to_update = collection_ref.where(email_field, '==', old_email).get()
            # Update each document with the new email
            for doc in docs_to_update:
                doc.reference.update({email_field: new_email})
        except Exception as e:
            # Log the error e, for example using logging library or print statement
            print(f"Error updating {collection_name}: {str(e)}")
            # Optionally, handle the error based on your application's requirements

    return "Updated"


def serialize_firestore_document(doc):
    # Convert a Firestore document to a dictionary, handling DatetimeWithNanoseconds
    doc_dict = doc.to_dict()
    for key, value in doc_dict.items():
        if isinstance(value, datetime):
            # Convert datetime to string (ISO format)
            doc_dict[key] = value.isoformat()
    return doc_dict


# Test on is user an admin
def is_admin(user):
    email = user.email
    info = get_user_info(email) or {}
    return user.is_authenticated and (user.is_staff or info['role'] == 'Admin')


@login_required
@user_passes_test(is_admin)
def admin_tools(request, feature_name):
    if feature_name == "manage_articles":
        from shop.views_scripts.manage_articles.create_article import create_article
        create_article(request)

    # Banner.objects.all().delete() # Функция чтобы удалять из бд данные
    # print(Banner.objects.all())
    articles = Article.objects.all().order_by('priority')
    context = {
        "feature_name": feature_name,
        "form": ArticleForm() if feature_name == "manage_articles" else "",
        "articles": articles
    }
    return render(request, 'admin_tools.html', context)


@login_required
@user_passes_test(is_admin)
def delete_users(request):
    if request.method == 'POST':
        try:
            # Load the user IDs from the request body
            data = json.loads(request.body)
            user_ids = data.get('userIds')

            if not user_ids:
                return JsonResponse({'status': 'error', 'message': 'No user IDs provided'}, status=400)

            emails_to_delete = []

            # Firestore has a limit of 500 operations per batch
            batch = db.batch()
            operations_count = 0

            for user_id in user_ids:
                # Query for documents with matching userId field

                docs = users_ref.where('userId', '==', int(user_id)).get()

                for doc in docs:
                    user_data = doc.to_dict()  # Convert document to dictionary
                    if 'email' in user_data:
                        emails_to_delete.append(user_data['email'])
                    doc_ref = users_ref.document(doc.id)
                    batch.delete(doc_ref)
                    operations_count += 1

                    # Commit the batch if it reaches the Firestore limit
                    if operations_count >= 500:
                        batch.commit()
                        batch = db.batch()  # Start a new batch
                        operations_count = 0

            if emails_to_delete:
                User.objects.filter(email__in=emails_to_delete).delete()

            # Commit any remaining operations in the batch
            if operations_count > 0:
                batch.commit()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def get_acc_data(email):
    existing_user = users_ref.where('email', '==', email).limit(1).stream()
    if existing_user:
        for user in existing_user:
            user_ref = users_ref.document(user.id)
            user_data = serialize_firestore_document(user_ref.get())
            user_info_dict = json.dumps(user_data)
            user_info_parsed = json.loads(user_info_dict)
            return user_info_dict, user_info_parsed
    return False, False


def fetch_document_name(item):
    if isinstance(item, str):
        item_ref = db.document(item)
    else:
        item_ref = item  # Assuming it's a document reference already
    doc = item_ref.get()
    return doc.to_dict() if doc.exists else None


def parallel_fetch_names(item_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        order_items_dict = list(executor.map(fetch_document_name, item_list))

    items = {}
    for item in order_items_dict:
        items[item.get("name")] = item
    return items

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'uaolimpiad/news/news_prototype.html'
    context_object_name = 'article'


def open_news(request, news_number):
    context = {}
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    return render(request, f'uaolimpiad/news/new_{news_number}.html', context)


def updateChatInfo(old_data, new_data):
    chats_query = chats_ref.where('userId', '==', old_data['userId']).get()

    all_tasks = {
        "9": {
            "1": "«Закільцьовані»",
            "2": "«І знов середня швидкість»",
            "3": "«Тиснемо-перетиснемо»",
            "4": "«Дрова і вода»",
            "5": "«Циліндр в акваріумі»",
        },
        "10": {
            "1": "«І знов середня швидкість»",
            "2": "«Як вимірюють період напіврозпаду»",
            "3": "«Вода»",
            "4": "«Мерефо-Херсонський міст»",
            "5": "«Лабораторна комашка»",
        },
        "11": {
            "1": "«Оптика циліндру»",
            "2": "«Молекула водню»",
            "3": "«Безпечні перевезення»",
            "4": "«Котимося вгору»",
            "5": "«Сферичний обігрівач»",
        }
    }
    for chat_doc in chats_query:
        this_chat = chat_doc.to_dict()  # Получаем содержимое документа
        chat_name = f"{new_data['firstname']} {new_data['lastname']} {new_data['paralel']} клас {all_tasks[new_data['paralel']][this_chat['task_name']]}"
        paralel_class = int(new_data['paralel'])
        # Обновляем документ с новым значением поля chat_name
        chats_ref.document(chat_doc.id).update({
            'chatName': chat_name,
            'class': paralel_class  # Добавляем поле class с числовым значением
        })
    messages_query = messages_ref.where('sender_id', '==', old_data['userId']).get()
    for message_doc in messages_query:
        message = message_doc.to_dict()
        message_sender_name = f"{new_data['firstname']} {new_data['lastname']}"
        messages_ref.document(message_doc.id).update({
            'sender_name': message_sender_name,
        })


def contact_us_page(request):
    context = {}
    email = get_user_session_type(request)
    context['role'] = get_user_role(email)
    user_info = get_user_info(email)

    if user_info is not None and "rights" in user_info:
        context['rights'] = user_info['rights']
    else:
        context['rights'] = None
    return render(request, "uaolimpiad/mainPages/contact_us.html")


def make_json_serializable(obj):
    if isinstance(obj, DocumentReference):
        # choose whichever you need on the client side:
        return obj.path       # or obj.id
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(v) for v in obj]
    else:
        return obj


def materials_view(request):
    materials_page = request.GET.get('page') or ""
    email = get_user_session_type(request)
    role = "Student"  # TODO: Тут нужно сделать логику взятия роли пользователя
    context = {
        "page_name": materials_page,
        "role": role,
    }
    return render(request, 'uaolimpiad/mainPages/materialsMain.html', context=context)
