# shop/firebase.py
import os
import firebase_admin
from firebase_admin import credentials, firestore

_app_inited = False


def get_firestore():
    global _app_inited
    if not _app_inited:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
        if not cred_path:
            raise RuntimeError("FIREBASE_CREDENTIALS env var is missing")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(cred_path), {
                "storageBucket": bucket
            })
        _app_inited = True
    return firestore.client()
