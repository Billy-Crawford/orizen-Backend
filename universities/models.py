# universities/models.py

from django.db import models
from users.models import CustomUser

# Statut de candidature
CANDIDATURE_STATUS = (
    ('pending', 'En attente'),
    ('accepted', 'Acceptée'),
    ('rejected', 'Rejetée'),
)

class University(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='universities/logos/', blank=True, null=True)
    contact_email = models.EmailField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='universities_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Filiere(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='filieres')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.university.name})"

class Candidature(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role':'student'})
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='candidatures')
    status = models.CharField(max_length=20, choices=CANDIDATURE_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidatures_reviewed')  # Conseiller qui a validé

    def __str__(self):
        return f"{self.student.username} → {self.filiere.name} [{self.status}]"
