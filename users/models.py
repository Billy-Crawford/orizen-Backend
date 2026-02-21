# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

# Définition des rôles
USER_ROLES = (
    ('student', 'Étudiant'),
    ('advisor', 'Conseiller'),
    ('university', 'Université'),
    ('admin', 'Admin'),
)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'role']

    def __str__(self):
        return f"{self.username} ({self.role})"
