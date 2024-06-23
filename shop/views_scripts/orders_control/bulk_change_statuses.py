import concurrent

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    is_admin, users_ref
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
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User

@login_required
@user_passes_test(is_admin)  # Adjust the test as needed
def change_statuses(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            orderIds = data.get('orderIds')
            newStatus = data.get('status')

            if not orderIds or not newStatus:
                return JsonResponse({"success": False, "message": "Order IDs or status not provided"}, status=400)

            allOrders = orders_ref.get()

            # Build a dictionary with 'order-id' or 'order_id' as the key, and the document snapshot as the value
            orderDict = {}
            for order in allOrders:
                orderData = order.to_dict()
                key = str(orderData.get('order-id') or orderData.get('order_id'))
                orderDict[key] = order

            # Update the documents that need to be changed
            for orderId in orderIds:
                orderId = str(orderId)
                if orderId in orderDict:
                    orderRef = orderDict[orderId].reference
                    orderRef.update({'Status': newStatus})

            return JsonResponse({"success": True, "message": "Order statuses updated successfully."})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)