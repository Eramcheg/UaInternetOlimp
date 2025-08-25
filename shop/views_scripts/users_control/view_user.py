import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from shop.views import get_user_category, serialize_firestore_document, users_ref, is_admin


@login_required
@user_passes_test(is_admin)
def view_user(request, user_id):
    print("View user " + user_id)

    existing_user = users_ref.where('userId', '==', int(user_id)).limit(1).stream()
    email = request.user.email
    context = {
        'feature_name': "view_user",
        'orders':[],
        'addresses': [],
    }

    for user in existing_user:
        user_ref = users_ref.document(user.id)
        user_data = serialize_firestore_document(user_ref.get())

        # Assuming user_data contains 'email', adjust if necessary
        user_email = user_data.get('email', '')

        # Fetch orders related to the user
        currencies_dict = {}

        context['currencies'] = currencies_dict

        context['addresses'] = []

        # Fetch cart items related to the user
        # Assuming cart collection documents contain user email, adjust if your schema is different
        cart_items = []

        context['cart'] = cart_items

        # User information - to_dict() can be used directly
        context['user_info'] = user_data

        # Convert user_data to JSON string if you need to pass it as a string in the context
        context['user_info_dict'] = json.dumps(user_data)
        print(context['cart'])
    return render(request, 'admin_tools.html', context)