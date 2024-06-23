import ast
import random
from datetime import datetime
from io import BytesIO
from random import randint

import concurrent.futures
import requests
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
import csv
import firebase_admin
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from celery import shared_task

from shop.forms import UserRegisterForm, User
from shop.views import addresses_ref, cart_ref, get_user_category, serialize_firestore_document, users_ref, is_admin, \
    orders_ref, itemsRef, db, process_items, get_order_items, single_order_ref
from shop.views import get_user_info
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

from PIL import Image as PILImage
@login_required
def download_csv_order(request, order_id):
    order_items = get_order_items(order_id)
    # Prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.csv"'.format(order_id)

    writer = csv.writer(response)
    writer.writerow(['product_number', 'quantity', 'price', 'total'])  # Writing the headers

    # Assuming 'list' contains the items in the order with 'name', 'quantity', 'price'
    for item in order_items:
        product_number = item.get('name')
        quantity = item.get('quantity')
        price = item.get('price')
        total = item.get('total')
        writer.writerow([product_number, quantity, price, total])

    return response

@login_required
def download_pdf_no_img(request, order_id):
    order_items = get_order_items(order_id)
    userEmail = order_items[0].get('emailOwner', "")
    info = {}
    if userEmail:
        info = get_user_info(userEmail) or {}
    client_name = info.get('first_name', "") + " " + info.get('last_name', "")
    buffer = BytesIO()

    # Basic setup
    styles = getSampleStyleSheet()

    center_bold_style2 = ParagraphStyle('CenterBold', parent=styles['Heading2'], fontSize=18, alignment=1,
                                        fontName='Times-Bold')
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, fontName='Times-Bold')
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    content = []
    content.append(Paragraph(f"Order N.: {order_id}", center_bold_style2))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Client name: {client_name}", bold_style))
    content.append(Paragraph(f"Client email: {userEmail}", bold_style))

    currency = "€" if info.get("currency", "Euro") == "Euro" else "$"

    table_data = [["Product", "Quantity", "Price per item", "Total"]]
    for item_order in order_items:

        row = [item_order['name'], item_order['quantity'], currency + str(item_order['price']),
               currency + str(round(item_order['price'] * item_order['quantity'], 2))]
        table_data.append(row)

    table = Table(table_data, colWidths=[1.7 * inch, 1.7 * inch, 1.7 * inch, 1.7 * inch, 1.3 * inch])

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

    # Order items table

    doc.build(content)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pdf_order_{order_id}_without_images.pdf"'
    response.write(pdf)

    return response


def get_optimized_image(url, output_size=(50, 50)):
    response = requests.get(url)
    image = PILImage.open(BytesIO(response.content))
    # image = image.resize(output_size, PILImage.Resampling.LANCZOS)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    byte_io = BytesIO()
    image.save(byte_io, 'JPEG')
    byte_io.seek(0)
    return byte_io


@login_required
# @user_passes_test(is_admin)
def download_pdf_w_img(request, order_id):

    order_items = get_order_items(order_id)
    userEmail = order_items[0].get('emailOwner', "")
    info = {}
    if userEmail:
        info = get_user_info(userEmail) or {}
    client_name = info.get('first_name', "") + " " + info.get('last_name', "")
    buffer = BytesIO()

    # Basic setup
    styles = getSampleStyleSheet()

    center_bold_style2 = ParagraphStyle('CenterBold', parent=styles['Heading2'], fontSize=18, alignment=1,
                                        fontName='Times-Bold')
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, fontName='Times-Bold')
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    content = []
    content.append(Paragraph(f"Order N.: {order_id}", center_bold_style2))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Client name: {client_name}", bold_style))
    content.append(Paragraph(f"Client email: {userEmail}", bold_style))

    currency = "€" if info.get("currency", "Euro") == "Euro" else "$"

    table_data = [["Product", "Image", "Quantity", "Price per item", "Total"]]

    for item_order in order_items:
        image_path = item_order['image-url'] if 'image-url' in item_order else item_order['image_url']
        optimized_image_io = get_optimized_image(image_path)

        # Convert the BytesIO object to a ReportLab Image object
        reportlab_image = Image(optimized_image_io)
        reportlab_image.drawHeight = 50  # Set the desired display height
        reportlab_image.drawWidth = 50  # Set the desired display width

        row = [item_order['name'], reportlab_image, item_order['quantity'],
               currency + str(item_order['price']),
               currency + str(round(item_order['price'] * item_order['quantity'], 2))]
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

    # Order items table

    doc.build(content)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pdf_order_{order_id}_with_images.pdf"'
    response.write(pdf)

    return response

def delete_documents_in_batches(query_snapshot):
    batch = db.batch()
    count = 0

    for doc in query_snapshot:
        batch.delete(doc.reference)
        count += 1
        # Commit the batch every 500 deletes
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()

    # Commit any remaining deletes in the batch
    if count % 500 != 0:
        batch.commit()

@login_required
@user_passes_test(is_admin)
def at_delete_order(request, order_id):
    order_id = int(order_id)
    orders_query = orders_ref.where('order_id', '==', order_id).get()
    if not orders_query:
        orders_query = orders_ref.where("`order-id`", '==', order_id).get()
    delete_documents_in_batches(orders_query)

    # Query and batch delete from "Order"
    order_items_query = single_order_ref.where('order_id', '==', order_id).get()
    if not order_items_query:
        order_items_query = single_order_ref.where("`order-id`", '==', order_id).get()
    delete_documents_in_batches(order_items_query)
    return HttpResponse(status=204)