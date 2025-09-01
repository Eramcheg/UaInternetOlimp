import hashlib
import random
import string
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from firebase_admin import firestore

from shop.forms import UserRegisterForm, User, SchoolRegistrationForm
from shop.views import users_ref, school_registrations_ref, get_user_info, get_user_session_type

CONSENT_VERSION = "v1.0-2025-09-01"


def generate_random_code(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def check_code_unique(code, collection_ref):
    query = collection_ref.where('user_id', '==', code).limit(1).stream()
    return any(query)


def get_unique_user_id():

    while True:
        new_user_id = generate_random_code()
        if not check_code_unique(new_user_id, users_ref):
            return new_user_id


def check_login_unique_in_firestore(login_name):
    query = users_ref.where('login', '==', login_name).limit(1).stream()
    return any(query)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data.get('email')
            login_name = form.cleaned_data.get('login')
            if check_login_unique_in_firestore(login_name):
                form.add_error('login', 'Логін вже використовується.')
                return render(request, 'registration/register.html', {'form': form})

                # Check if login is unique in Django's database
            if User.objects.filter(username=login_name).exists():
                form.add_error('login', 'Логін вже використовується.')
                return render(request, 'registration/register.html', {'form': form})
            paralel = form.cleaned_data.get('paralel_number')
            if paralel not in ["9", "10", "11"]:
                form.add_error('login', 'Неіснуюча паралель.')
                return render(request, 'registration/register.html', {'form': form})
            existing_user = users_ref.where('email', '==', email).limit(1).get()

            if list(existing_user):  # Convert to list to check if it's non-empty
                print('Error: User with this Email already exists.')
                form.add_error('email', 'Користувач з таким емейлем вже існує.')
                return render(request, 'registration/register.html', {'form': form})
            else:

                user_id = get_unique_user_id()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                third_name = form.cleaned_data.get('third_name')
                school = form.cleaned_data.get('school')

                phone = form.cleaned_data.get('phone_number')

                new_user = {
                    'Enabled': 'True',
                    "login": login_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'third_name': third_name,
                    'email': email,
                    'school': school,
                    'paralel': paralel,
                    'phone': phone,
                    'registrationDate': current_time,
                    'role': "Student",
                    'userId': user_id,
                }
                users_ref.add(new_user)

                user = form.save(commit=False)
                user.username = login_name  # Set the username to be the login field
                user.save()  # Now save the user to the database

                password = form.cleaned_data.get('password1')
                form.save()
                user = authenticate(username=login_name, password=password)
                if user:
                    login(request, user)
                    return redirect('home')
    else:
        form = UserRegisterForm()

    print(form.errors)
    return render(request, 'registration/register.html', {'form': form, 'errors': form.errors})


def _email_fingerprint(email: str) -> str:
    # стабильный doc_id для гостя
    return "anon_" + hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:24]


def school_registration(request):
    try:
        email_from_session = get_user_session_type(request)  # может вернуть None
    except Exception:
        email_from_session = None
    try:
        info = get_user_info(email_from_session) if email_from_session else {}
    except Exception:
        info = {}
    user_id = info.get('userId')

    if user_id:
        if school_registrations_ref.document(user_id).get().exists:
            return redirect("school_registration_success")

    initial = {
        "contactEmail": (email_from_session or ""),
        "paralel": info.get('paralel', '8'),
    }

    if request.method == 'POST':
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if user_id:
                doc_id = user_id
            else:
                contact_email = cd["contactEmail"].strip().lower()
                if not contact_email:
                    messages.error(request, "Вкажіть email.")
                    return render(request, 'registration/school_registration.html', {'form': form})
                doc_id = _email_fingerprint(contact_email)
                existing_by_email = (school_registrations_ref
                                     .where('contactEmail', '==', contact_email)
                                     .limit(1).stream())
                if any(existing_by_email):
                    return redirect("school_registration_success")

            payload = {
                "schemaVersion": 1,
                "status": "submitted",
                "userId": doc_id,

                # ПІБ
                "lastName_uk": cd["lastName_uk"],
                "firstName_uk": cd["firstName_uk"],
                "patronymic_uk": cd.get("patronymic_uk") or "",
                "lastName_en": cd["lastName_en"],
                "firstName_en": cd["firstName_en"],
                "patronymic_en": cd.get("patronymic_en") or "",

                # Школа в Україні / за кордоном
                "studyInUkraine": bool(cd["studyInUkraine"]),
                "schoolOblast": cd.get("schoolOblast") or "",
                "schoolNumber": cd.get("schoolNumber") or "",
                "schoolName": cd.get("schoolName") or "",
                "studyAbroadNote": "" if cd["studyInUkraine"] else "Навчаюсь за кордоном",

                # Проживання
                "residenceCity": cd["residenceCity"],
                "residenceCountry": cd["residenceCountry"],

                # Контакти
                "contactEmail": cd["contactEmail"],
                "contactLinks": cd["contactLinks"],

                # Паралель (рядок!)
                "paralel": str(cd["paralel"]),

                # Олімпіади
                "olympiadsParticipation": bool(cd["olympiadsParticipation"]),
                "olympiadsSubjects": cd.get("olympiadsSubjects") or [],
                "olympiadsAchievements": cd.get("olympiadsAchievements") or "",

                # Група
                "plannedGroup": cd["plannedGroup"],

                # Нова пошта
                "npRecipientFullName": cd["npRecipientFullName"],
                "npPhone": cd["npPhone"],
                "npCity": cd["npCity"],
                "npBranchNumber": cd["npBranchNumber"],

                # Згода
                "consentGiven": True,
                "consentTextVersion": CONSENT_VERSION,
                "consentGivenAt": firestore.SERVER_TIMESTAMP,

                # Службові
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
            school_registrations_ref.document(doc_id).set(payload, merge=True)

            messages.success(request, "Анкету надіслано. Дякуємо!")
            return redirect("school_registration_success")
    else:
        form = SchoolRegistrationForm(initial=initial)

    return render(request, 'registration/school_registration.html', {'form': form, 'errors': form.errors})


def school_registration_success(request):
    return render(request, 'registration/school_registration_success.html')

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