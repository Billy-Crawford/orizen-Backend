# documents/models.py

from django.db import models
from django.conf import settings
from universities.models import Filiere

class Document(models.Model):

    DOCUMENT_TYPES = (
        ("cv", "CV"),
        ("bulletin", "Bulletin"),
        ("photo", "Photo"),
        ("other", "Autre"),
    )

    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("validated", "Validé"),
        ("rejected", "Rejeté"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to="documents/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_documents",
        limit_choices_to={'role': 'advisor'}
    )

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.document_type} ({self.status})"