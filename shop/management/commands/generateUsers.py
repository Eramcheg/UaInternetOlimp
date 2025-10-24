import os
from typing import Dict, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

import firebase_admin
from firebase_admin import credentials, firestore


User = get_user_model()


def init_firebase():
    """Инициализация Firebase Admin из переменной окружения FIREBASE_CREDENTIALS."""
    if firebase_admin._apps:
        return
    cred_path = os.environ.get("FIREBASE_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        raise SystemExit(
            "Set FIREBASE_CREDENTIALS to absolute path of Firebase service-account JSON"
        )
    firebase_admin.initialize_app(credentials.Certificate(cred_path))


def random_password(length: int = 12) -> str:
    # Только буквы и цифры, без похожих символов (0/O, 1/l/I).
    allowed = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789!@"
    return get_random_string(length=length, allowed_chars=allowed)


def normalize_username(raw: str, fallback_email: str | None = None) -> str:
    if raw:
        u = str(raw).strip()
    else:
        raise ValueError("Cannot build username: both username and email are empty")
    # Django ограничение по умолчанию — 150 символов
    return u[:150]


class Command(BaseCommand):
    help = (
        "Импортирует пользователей из Firestore коллекции 'users' в Django. "
        "Создаёт/обновляет пользователя по username, задаёт случайный пароль."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--collection",
            default="users",
            help="Имя коллекции Firestore (по умолчанию 'users')",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать, что будет сделано, без изменений в БД",
        )
        parser.add_argument(
            "--print-passwords",
            action="store_true",
            help="Вывести сгенерированные пароли (осторожно: секретные данные!)",
        )

    def handle(self, *args, **opts):
        init_firebase()
        coll_name: str = opts["collection"]
        dry_run: bool = opts["dry_run"]
        print_pw: bool = opts["print_passwords"]

        db = firestore.client()
        users_ref = db.collection(coll_name)

        created = 0
        updated = 0
        skipped = 0

        # stream() — ленивый итератор по документам
        for doc in users_ref.stream():
            data: Dict[str, Any] = doc.to_dict() or {}

            fb_username = (data.get("login") or "").strip()
            email = (data.get("email") or "").strip().lower() or None
            first_name = (data.get("first_name") or "").strip()
            last_name = (data.get("last_name") or "").strip()

            # username обязателен (если нет — пробуем из email)
            try:
                username = normalize_username(fb_username, email)
            except ValueError:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skip doc {doc.id}: no username/email in Firestore"
                    )
                )
                skipped += 1
                continue

            # Подготовим поля
            defaults = dict(
                email=email or "",
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

            # Создать/обновить
            user, was_created = User.objects.get_or_create(
                username=username,
                defaults=defaults,
            )

            if was_created:
                pwd = random_password()
                if not dry_run:
                    user.set_password(pwd)
                    user.save()
                created += 1
                msg = f"[CREATED] {username} <{email or '-'}>"
                if print_pw:
                    msg += f"  password={pwd}"
                self.stdout.write(self.style.SUCCESS(msg))
            else:
                changed = False
                # Обновим поля, если изменились
                if email and user.email != email:
                    user.email = email
                    changed = True
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    changed = True
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    changed = True
                if not user.is_active:
                    user.is_active = True
                    changed = True

                if changed:
                    if not dry_run:
                        user.save()
                    updated += 1
                    self.stdout.write(self.style.NOTICE(f"[UPDATED] {username}"))
                else:
                    self.stdout.write(f"[SKIP] {username} (no changes)")

        summary = f"Created: {created}, Updated: {updated}, Skipped: {skipped}"
        if dry_run:
            summary = "[DRY-RUN] " + summary
        self.stdout.write(self.style.SUCCESS(summary))