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

# CANDIDATURE

class Candidature(models.Model):

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name="candidatures"
    )

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name='candidatures'
    )

    # Statut université uniquement
    status = models.CharField(
        max_length=20,
        choices=CANDIDATURE_STATUS,
        default='pending'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    # 🔵 Conseiller associé (si existe)
    advisor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'advisor'},
        related_name="advisor_candidatures"
    )

    # 🔵 Le dossier a-t-il été validé par le conseiller ?
    advisor_approved = models.BooleanField(default=False)

    # 🔴 Université qui a pris la décision finale
    reviewed_by_university = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'university'},
        related_name="reviewed_candidatures"
    )

    def __str__(self):
        advisor_info = self.advisor.username if self.advisor else "No Advisor"
        return f"{self.student.username} → {self.filiere.name} [{self.status}] ({advisor_info})"


# class Candidature(models.Model):
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role':'student'})
#     filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='candidatures')
#     status = models.CharField(max_length=20, choices=CANDIDATURE_STATUS, default='pending')
#     submitted_at = models.DateTimeField(auto_now_add=True)
#     reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidatures_reviewed')  # Conseiller qui a validé
#
#     submitted_by_advisor = models.BooleanField(default=False)
#
#     advisor = models.ForeignKey(
#         CustomUser,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         limit_choices_to={'role': 'advisor'},
#         related_name="submitted_candidatures"
#     )
#
#     def __str__(self):
#         return f"{self.student.username} → {self.filiere.name} [{self.status}]"


# Notifications
class Notification(models.Model):
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,  # ce que tu avais déjà
        null=True,                   # ✅ ajoute cette ligne
        blank=True                   # optionnel, mais recommandé pour admin/forms
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    # Historique
class ActionHistory(models.Model):
    ACTION_TYPES = [
        ("create_university", "Create University"),
        ("create_filiere", "Create Filiere"),
        ("submit_candidature", "Submit Candidature"),
        ("update_status", "Update Candidature Status"),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="history")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.created_at}"