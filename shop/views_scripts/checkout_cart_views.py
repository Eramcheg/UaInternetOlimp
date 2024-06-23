import concurrent
import csv

from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from background_task import background

from shop.decorators import login_required_or_session, logout_required
from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    get_user_category, get_user_session_type, metadata_ref, users_ref, update_email_in_db, get_user_prices
import ast
import random
from datetime import datetime
from random import randint
from reportlab.platypus import Image
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
from django.core.mail import send_mail, EmailMessage

from shop.forms import UserRegisterForm, User
import os
import json
import time
import logging
import tempfile
from datetime import datetime, timedelta
from subprocess import run
from io import BytesIO, StringIO
import urllib.request
import ftplib
from django.views.generic import TemplateView
# Django imports
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

# Third-party imports

import firebase_admin
from firebase_admin import credentials, firestore
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from shop.views_scripts.auth_views import get_new_user_id
from shop.views_scripts.profile_views import get_user_addresses

vats = {'Afghanistan': 0, 'Åland Islands': 0, 'Albania': 0, 'Algeria': 0, 'American Samoa': 0, 'Andorra': 0, 'Angola': 0, 'Anguilla': 0, 'Antarctica': 0, 'Antigua and Barbuda': 0, 'Argentina': 0, 'Armenia': 0, 'Aruba': 0, 'Australia': 0, 'Austria': 20, 'Azerbaijan': 0, 'Bahamas': 0, 'Bahrain': 0, 'Bangladesh': 0, 'Barbados': 0, 'Belarus': 0, 'Belgium': 21, 'Belize': 0, 'Benin': 0, 'Bermuda': 0, 'Bhutan': 0, 'Bolivia': 0, 'Bosnia and Herzegovina': 0, 'Botswana': 0, 'Bouvet Island': 0, 'Brazil': 0, 'British Indian Ocean Territory': 0, 'Brunei': 0, 'Bulgaria': 20, 'Burkina Faso': 0, 'Burma (Myanmar)': 0, 'Burundi': 0, 'Cambodia': 0, 'Cameroon': 0, 'Canada': 0, 'Cape Verde': 0, 'Cayman Islands': 0, 'Central African Republic': 0, 'Chad': 0, 'Chile': 0, 'China': 0, 'Christmas Island': 0, 'Cocos (Keeling) Islands': 0, 'Colombia': 0, 'Comoros': 0, 'Congo, Dem. Republic': 0, 'Congo, Republic': 0, 'Cook Islands': 0, 'Costa Rica': 0, 'Croatia': 25, 'Cuba': 0, 'Cyprus': 19, 'Czech Republic': 21, 'Denmark': 25, 'Djibouti': 0, 'Dominica': 0, 'Dominican Republic': 0, 'East Timor': 0, 'Ecuador': 0, 'Egypt': 0, 'El Salvador': 0, 'Equatorial Guinea': 0, 'Eritrea': 0, 'Estonia': 22, 'Ethiopia': 0, 'Falkland Islands': 0, 'Faroe Islands': 0, 'Fiji': 0, 'Finland': 24, 'France': 20, 'French Guiana': 0, 'French Polynesia': 0, 'French Southern Territories': 0, 'Gabon': 0, 'Gambia': 0, 'Georgia': 0, 'Germany': 19, 'Ghana': 0, 'Gibraltar': 0, 'Greece': 24, 'Greenland': 0, 'Grenada': 0, 'Guadeloupe': 0, 'Guam': 0, 'Guatemala': 0, 'Guernsey': 0, 'Guinea': 0, 'Guinea-Bissau': 0, 'Guyana': 0, 'Haiti': 0, 'Heard Island and McDonald Islands': 0, 'Honduras': 0, 'HongKong': 0, 'Hungary': 27, 'Iceland': 0, 'India': 0, 'Indonesia': 0, 'Iran': 0, 'Iraq': 0, 'Ireland': 23, 'Israel': 0, 'Italy': 22, 'Ivory Coast': 0, 'Jamaica': 0, 'Japan': 0, 'Jersey': 0, 'Jordan': 0, 'Kazakhstan': 0, 'Kenya': 0, 'Kiribati': 0, 'Dem. Republic of Korea': 0, 'Kuwait': 0, 'Kyrgyzstan': 0, 'Laos': 0, 'Latvia': 21, 'Lebanon': 0, 'Lesotho': 0, 'Liberia': 0, 'Libya': 0, 'Liechtenstein': 8.1, 'Lithuania': 21, 'Luxemburg': 0, 'Macau': 0, 'Macedonia': 0, 'Madagascar': 0, 'Malawi': 0, 'Malaysia': 0, 'Maldives': 0, 'Mali': 0, 'Malta': 18, 'Man Island': 0, 'Marshall Islands': 0, 'Martinique': 0, 'Mauritania': 0, 'Mauritius': 0, 'Mayotte': 0, 'Mexico': 0, 'Micronesia': 0, 'Moldova': 0, 'Monaco': 20, 'Mongolia': 0, 'Montenegro': 0, 'Montserrat': 0, 'Morocco': 0, 'Mozambique': 0, 'Namibia': 0, 'Nauru': 0, 'Nepal': 0, 'Netherlands': 21, 'Netherlands Antilles': 0, 'New Caledonia': 0, 'New Zealand': 0, 'Nicaragua': 0, 'Niger': 0, 'Nigeria': 0, 'Niue': 0, 'Norfolk Island': 0, 'Northern Ireland': 0, 'Northern Mariana Islands': 0, 'Norway': 0, 'Oman': 0, 'Pakistan': 0, 'Palau': 0, 'Palestinian Territories': 0, 'Panama': 0, 'Papua New Guinea': 0, 'Paraguay': 0, 'Peru': 0, 'Philippines': 0, 'Pitcairn': 0, 'Poland': 23, 'Portugal': 23, 'Puerto Rico': 0, 'Qatar': 0, 'Reunion Island': 0, 'Romania': 19, 'Russian Federation': 0, 'Rwanda': 0, 'Saint Barthelemy': 0, 'Saint Kitts and Nevis': 0, 'Saint Lucia': 0, 'Saint Martin': 0, 'Saint Pierre and Miquelon': 0, 'Saint Vincent and the Grenadines': 0, 'Samoa': 0, 'San Marino': 0, 'São Tomé and Príncipe': 0, 'Saudi Arabia': 0, 'Senegal': 0, 'Serbia': 0, 'Seychelles': 0, 'Sierra Leone': 0, 'Singapore': 0, 'Slovakia': 20, 'Slovenia': 22, 'Solomon Islands': 0, 'Somalia': 0, 'South Africa': 0, 'South Georgia and the South Sandwich Islands': 0, 'South Korea': 0, 'Spain': 21, 'Sri Lanka': 0, 'Sudan': 0, 'Suriname': 0, 'Svalbard and Jan Mayen': 0, 'Swaziland': 0, 'Sweden': 25, 'Switzerland': 8.1, 'Syria': 0, 'Taiwan': 0, 'Tajikistan': 0, 'Tanzania': 0, 'Thailand': 0, 'Togo': 0, 'Tokelau': 0, 'Tonga': 0, 'Trinidad and Tobago': 0, 'Tunisia': 0, 'Turkey': 0, 'Turkmenistan': 0, 'Turks and Caicos Islands': 0, 'Tuvalu': 0, 'Uganda': 0, 'Ukraine': 0, 'United Arab Emirates': 0, 'United Kingdom': 20, 'United States': 0, 'Uruguay': 0, 'Uzbekistan': 0, 'Vanuatu': 0, 'Vatican City State': 0, 'Venezuela': 0, 'Vietnam': 0, 'Virgin Islands (British)': 0, 'Virgin Islands (U.S.)': 0, 'Wallis and Futuna': 0, 'Western Sahara': 0, 'Yemen': 0, 'Zambia': 0, 'Zimbabwe': 0}


@login_required_or_session
def cart_page(request):
    email = get_user_session_type(request)
    category, currency = get_user_prices(request, email)
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    context = {
        'documents': sorted(get_cart(email), key=lambda x: x['number']),
        'currency': currency
    }
    return render(request, 'cart.html', context=context)


def sort_documents(request):
    order_by = request.GET.get('order_by', 'name')
    direction = request.GET.get('direction', 'asc')

    # Get documents from Firebase
    documents = get_cart(request.user.email)

    if order_by == 'sum':
        key_function = lambda x: x.get('price', 0) * x.get('quantity', 0)
    else:
        key_function = lambda x: x.get(order_by, "")

    sorted_documents = sorted(documents, key=key_function, reverse=(direction == 'desc'))

    return JsonResponse({'documents': sorted_documents})

@login_required
def send_email(request):
    if request.method == 'POST':
        # Создаю order
        data = json.loads(request.body)
        vat = int(data.get('vat', 0))/100

        user_email = request.user.email
        category, currency = get_user_category(user_email) or ("Default", "Euro")

        currency = '€' if currency == 'Euro' else '$'

        cart = get_cart(user_email)

        order_id = randint(1000000, 100000000)
        item_refs = []
        all_orders_info = []
        names = []
        sum = 0

        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerow(['name', 'quantity'])

        for order_item in cart:
            description = order_item.get('description')
            price = order_item.get('price')
            quantity = order_item.get('quantity')
            name = order_item.get('name')
            names.append(name)
            image_url = order_item.get('image_url')
            sum += round(price * quantity, 1)
            new_order_item = {
                'description': description,
                "emailOwner": user_email,
                'image_url': image_url,
                'image-url': image_url,
                "name": name,
                "order_id": order_id,
                "order-id": order_id,
                "price": price,
                "quantity": quantity,
            }
            all_orders_info.append(new_order_item)
            doc_ref = single_order_ref.document()
            doc_ref.set(new_order_item)
            item_refs.append(doc_ref)

            csv_writer.writerow([name, quantity])

        csv_output.seek(0)
        csv_content = csv_output.getvalue()
        csv_output.close()

        new_order = {
            'Status': 'Awaiting',
            'date': datetime.now(),  # Current date and time
            'email': user_email,
            'list': [ref.path for ref in item_refs],  # Using document paths as references
            'order_id': order_id,
            'order-id': order_id,
            'price': round(sum, 1),
            'currency': 'Euro',
        }
        orders_ref.add(new_order)
        new_order['date'] = new_order['date'].isoformat()
        email_process(all_orders_info, new_order, currency, vat, user_email, order_id, csv_content, request.user.first_name + " "+ request.user.last_name)
        clear_all_cart(user_email)
        return JsonResponse({'status': 'success', 'redirect_name': 'home'})
    return JsonResponse({'status': 'error'}, status=400)


@background(schedule=60)
def email_process(all_orders_info, new_order, currency, vat, user_email, order_id, csv_content, name):
    try:
        pdf_response = receipt_generator(all_orders_info, new_order, name, currency, vat)

        subject = 'Your Order Receipt'
        server_mail_subject = f"{user_email} just ordered"
        email_body = 'Thank you for your order! Here is your receipt! Detailed Information about your order you can find in your profile.'
        server_email_body = f'Here is {user_email} order info:'
        recipient_list = [user_email]

        recipient_list_server = ['westadatabase@gmail.com']

        email = EmailMessage(subject, email_body, settings.EMAIL_HOST_USER, recipient_list)

        emailServer = EmailMessage(server_mail_subject, server_email_body, settings.EMAIL_HOST_USER, recipient_list_server)
        email.attach(f'order_receipt_{order_id}.pdf', pdf_response, 'application/pdf')
        emailServer.attach(f'order_{order_id}.csv', csv_content, 'text/csv')
        emailServer.attach(f'order_receipt_{order_id}.pdf', pdf_response, 'application/pdf')
        email.send()
        emailServer.send()
    except Exception as e:
        print(f"Failed to process email: {str(e)}")

def clear_all_cart(email):
    # Assuming `cart_ref` is defined and accessible within this scope
    docs = cart_ref.where('emailOwner', '==', email).stream()
    for doc in docs:
        doc.reference.delete()

def receipt_generator(orders, order, name, currency, vat):
    # Assuming 'orders' contains the list of items in the cart
    # and 'order' contains details about the order itself
    buffer = BytesIO()

    # Basic setup
    styles = getSampleStyleSheet()

    center_bold_style = ParagraphStyle('CenterBold', parent=styles['Normal'], fontSize=12, alignment=1,
                                       fontName='Times-Bold')
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, fontName='Times-Bold')
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    content = []
    title_style = styles['Heading1']
    content.append(Paragraph("OLIVER WEBER COLLECTION", title_style))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Client name: {name}", bold_style))

    table_data = [["Product", "Image", "Quantity", "Price per item", "Total"]]
    for item_order in orders:
        image_path = item_order['image-url']  # Adjust this line to get the actual image path or object
        image = Image(image_path)
        image.drawHeight = 50  # Example height in points
        image.drawWidth = 50
        row = [item_order['name'], image, item_order['quantity'], currency + str(item_order['price']), currency + str(round(item_order['price'] * item_order['quantity'], 2))]
        table_data.append(row)

    table = Table(table_data, colWidths=[1.7 * inch, 1.0 * inch, 1.0 * inch, 1.7 * inch, 1.3 * inch])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000')
    ])
    table.setStyle(table_style)
    content.append(Spacer(1, 1 * cm))

    content.append(table)

    # Order details
    email = order.get('email', 'No email provided')
    date_str = order['date']
    date_obj = datetime.fromisoformat(date_str)

    # Теперь применяем форматирование
    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    total_price = round(order.get('price', 0), 2)
    content.append(Spacer(1, 0.5 * inch))
    content.append(Paragraph(f"Total to pay(incl. VAT): {currency}{total_price}", bold_style))
    # content.append(Paragraph(f"Included VAT: {currency}{round(order['price'] * vat,2)}", bold_style))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Date: {formatted_date}", center_bold_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"E-mail: {email}", center_bold_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"DOCUMENT N.: {get_check_id()}", center_bold_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph("Thank you for your purchase!", center_bold_style))

    doc.build(content)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.get("order_id", "unknown")}.pdf"'
    response.write(pdf)

    return pdf

def get_check_id():
    @firestore.transactional
    def increment_check_id(transaction, check_counter_ref):
        snapshot = check_counter_ref.get(transaction=transaction)
        last_check_id = snapshot.get('lastCheck') if snapshot.exists else 10000
        new_check_id = last_check_id + 1
        transaction.update(check_counter_ref, {'lastCheck': new_check_id})
        return new_check_id

    check_counter_ref = metadata_ref.document('checkCounter')
    transaction = db.transaction()
    new_check_id = increment_check_id(transaction, check_counter_ref)
    return new_check_id

@logout_required
def anonym_cart_info(request):

    email = get_user_session_type(request)
    category, currency = get_user_prices(request,email)
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    context = {
        'documents': sorted(get_cart(email), key=lambda x: x['number']),
        'currency': currency,
        'form_register':form_register,
        'form_login':form_login
    }
    print(context['documents'])

    return render(request, 'orderAnonymously.html', context=context)



def login_anonym_cart_info(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        email1 = get_user_session_type(request)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                email2 = form.cleaned_data.get('email') or user.email

                # Query Firebase Firestore to check the user's Enabled status
                firebase_user_doc = users_ref.where('email', '==', email2).limit(1).get()
                if firebase_user_doc and firebase_user_doc[0].to_dict().get('Enabled', True) == False:
                    # Redirect to home with an error message
                    messages.error(request, "Your account was disabled")
                    form.add_error(None, "Your account was disabled")
                    return render(request, 'orderAnonymously.html', {'form': form})
                else:
                    # Proceed to log the user in
                    clear_all_cart(email2)
                    login(request, user)
                    update_email_in_db(email1, email2)
                    return redirect('checkout_addresses')


def register_anonym_cart_info(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        email1 = get_user_session_type(request)
        if form.is_valid():

            email2 = form.cleaned_data.get('email')

            existing_user = users_ref.where('email', '==', email2).limit(1).get()

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
                category, currency = get_user_prices(request, email2)
                new_user = {
                    'Enabled': 'True',
                    "display_name": "undefined",
                    'social_title': social_title,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email2,
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

                username = email2
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
                    clear_all_cart(email2)
                    login(request, user)
                    update_email_in_db(email1, email2)
                    return redirect('checkout_addresses')


def checkout_addresses(request):
    email = get_user_session_type(request)
    addresses, addresses_dict = get_user_addresses(email)

    category, currency = get_user_category(email) or ("Default", "Euro")
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    context = {
               'documents': sorted(get_cart(email), key=lambda x: x['number']),
               'currency': currency,
               'form_register': form_register,
               'form_login': form_login,
               'my_addresses': addresses,
               'addresses_dict': addresses_dict
            }
    return render(request, 'orderAnonymAddresses.html', context=context)