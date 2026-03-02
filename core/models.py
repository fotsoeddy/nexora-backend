"""
BaseModel — Classe mère de tous les modèles du projet Nexora.

Centralise les attributs communs :
- id    : clé primaire auto-incrémentée (BigAutoField via DEFAULT_AUTO_FIELD)
- uuid  : identifiant universel unique pour l'exposition externe
- created_at / updated_at : timestamps automatiques
- is_active : désactivation logique (soft disable)
"""

import uuid as _uuid

from django.db import models


class BaseModel(models.Model):
    """
    Modèle abstrait de base.

    Tous les modèles métier du projet DOIVENT hériter de cette classe.
    Le champ `id` (BigAutoField) est automatiquement fourni par Django
    grâce au réglage DEFAULT_AUTO_FIELD dans settings.
    """

    uuid = models.UUIDField(
        default=_uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name="UUID",
        help_text="Identifiant universel unique exposé à l'extérieur.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Actif",
        help_text="Désactivation logique — les données ne sont pas supprimées.",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.pk})"

    def soft_delete(self) -> None:
        """Désactive l'entité au lieu de la supprimer physiquement."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def restore(self) -> None:
        """Réactive l'entité après un soft_delete."""
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
