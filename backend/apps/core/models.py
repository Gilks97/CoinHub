"""
Core base models shared across all CoinHub apps.
"""
import uuid
from django.db import models


class TimestampedModel(models.Model):
    """Abstract base that adds created_at and updated_at to every model."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
