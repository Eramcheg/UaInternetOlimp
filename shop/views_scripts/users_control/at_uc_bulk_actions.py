import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

from shop.views import db, is_admin, users_ref


@login_required
@user_passes_test(is_admin)  # Adjust the test as needed
def enable_users(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_ids = data.get('userIds')
            if user_ids is None:
                raise ValueError("User IDs not provided")

            # Call the helper function to enable users
            update_user_enabled_status(user_ids, True)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
@user_passes_test(is_admin)
def disable_users(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_ids = data.get('userIds')
            if user_ids is None:
                raise ValueError("User IDs not provided")

            # Call the helper function to disable users
            update_user_enabled_status(user_ids, False)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def update_user_enabled_status(user_ids, enable):
    """
    Updates the 'Enabled' status of users in Firestore based on provided user IDs.
    """
    batch_limit = 500
    batch_count = 0
    batch = db.batch()

    for user_id in user_ids:
        docs = users_ref.where('userId', '==', user_id).get()
        for doc in docs:
            doc_ref = users_ref.document(doc.id)
            batch.update(doc_ref, {"Enabled": enable})
            batch_count += 1

            if batch_count >= batch_limit:
                batch.commit()
                batch = db.batch()
                batch_count = 0

    if batch_count > 0:
        batch.commit()

    return True