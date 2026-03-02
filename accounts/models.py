import uuid as _uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé.

    Hérite d'AbstractUser (qui fournit déjà id, is_active, date_joined).
    On ajoute uuid pour l'exposition externe, et les champs métier.
    """

    username = None

    uuid = models.UUIDField(
        default=_uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name="UUID",
        help_text="Identifiant universel unique exposé à l'extérieur.",
    )
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
