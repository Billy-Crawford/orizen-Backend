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



class AdvisorStudentRelation(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="advisor_requests",
        limit_choices_to={'role': 'student'}
    )

    advisor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student_requests",
        limit_choices_to={'role': 'advisor'}
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    # EMpecher pluseurs conseillers acceptes
    def save(self, *args, **kwargs):
        if self.status == "accepted":
            existing = AdvisorStudentRelation.objects.filter(
                student=self.student,
                status="accepted"
            ).exclude(id=self.id)

            if existing.exists():
                raise ValueError("Student already has an accepted advisor.")

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("student", "advisor")

    def __str__(self):
        return f"{self.student.username} → {self.advisor.username} ({self.status})"
