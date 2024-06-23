import random
from django.shortcuts import render, redirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from shop.views import addresses_ref, country_dict, users_ref, get_user_category, get_user_prices


@login_required
def delete_address(request, address_id):
    if request.method != 'POST':
        return render(request, 'profile/profile_addresses.html', {'feature_name': 'new_address'})

    try:
        address_to_delete = addresses_ref.where('address_id', '==', address_id).limit(1).get()
        if not address_to_delete:
            return JsonResponse({'status': 'error', 'message': 'Address not found.'}, status=404)

        for address in address_to_delete:
            address_ref = addresses_ref.document(address.id)
            address_ref.delete()
        return JsonResponse({'status': 'success', 'message': 'Address deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def generate_unique_address_id():
    while True:
        # Generate a random 8-digit number
        address_id = random.randint(10000000, 99999999)

        # Check if this ID is already in use
        existing_address = addresses_ref.where('address_id', '==', address_id).get()

        # If the ID is not in use, it's unique, and we can return it
        if not existing_address:
            return address_id


@csrf_exempt
@login_required
def create_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_data = data.get('address_data')
            if not new_data:  # Check if new_data is None or empty
                return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)
            unique_address_id = generate_unique_address_id()

            address_document = {
                'address_name': new_data['alias'],
                'first_name': new_data['firstname'],
                'last_name': new_data['lastname'],
                'company': new_data['company'],
                'real_address': new_data['address1'],
                'address_complement': new_data['address2'],
                'postal_code': new_data['postcode'],
                'city': new_data['city'],
                'country': country_dict[new_data['id_country']],
                'phone': new_data['phone'],
                'email': request.user.email,
                'address_id': f"{unique_address_id}"
            }
            addresses_ref.add(address_document)
            return JsonResponse({'status': 'success', 'message': 'Address updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    email = request.user.email

    # Check for existing user by email
    existing_users = users_ref.where('email', '==', email).limit(1).get()
    ref = ""
    if existing_users:
        for user in existing_users:
            ref = users_ref.document(user.id)
    email = request.user.email
    category, currency = get_user_prices(request, email)
    currency = '€' if currency == 'Euro' else '$'
    context = {
        'feature_name': 'new_address',
        'user_ref': ref.get().to_dict(),
        'currency':currency
    }
    return render(request, 'profile.html', context=context)


@login_required
def update_address(request, address_id):
    email = request.user.email
    category, currency = get_user_prices(request,email)
    currency = '€' if currency == 'Euro' else '$'
    existing_address = addresses_ref.where('address_id', '==', address_id).limit(1).get()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_data = data.get('new')
            if existing_address:
                for address in existing_address:
                    address_ref = addresses_ref.document(address.id)
                    address_ref.update({
                        'address_name': new_data['alias'],
                        'first_name': new_data['firstname'],
                        'last_name': new_data['lastname'],
                        'company': new_data['company'],
                        'real_address': new_data['address1'],
                        'address_complement': new_data['address2'],
                        'postal_code': new_data['postcode'],
                        'city': new_data['city'],
                        'country': country_dict[new_data['id_country']],
                        'phone': new_data['phone'],
                    })
                return JsonResponse({'status': 'success', 'message': 'Address updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    if existing_address:
        address_dict = {}
        for address in existing_address:
            address_ref = addresses_ref.document(address.id)
            address_dict = address_ref.get().to_dict()
        context = {
            'feature_name': 'update_address',
            'address': address_dict,
            'currency':currency,
            'address_dict': json.dumps(address_dict),
        }
        # print(address_dict)
        return render(request, 'profile.html', context=context)
    return JsonResponse({'status': 'error'}, status=400)
