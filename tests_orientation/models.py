# tests_orientation/models.py
from django.db import models
from django.conf import settings
from universities.models import Filiere
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


# ============================
# QUESTION
# ============================

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:60]

# ============================
# TRAITS RIASEC
# ============================

class Trait(models.Model):
    code = models.CharField(max_length=1)   # R, I, A, S, E, C
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} - {self.name}"
# ============================
# CHOIX DE REPONSE
# ============================

class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"


# ============================
# SCORE D’UNE REPONSE PAR FILIERE
# ============================

# class ChoiceScore(models.Model):
#     choice = models.ForeignKey(
#         Choice,
#         on_delete=models.CASCADE,
#         related_name="scores"
#     )
#     filiere = models.ForeignKey(
#         Filiere,
#         on_delete=models.CASCADE,
#         related_name="orientation_scores"
#     )
#     score = models.IntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.choice.text} → {self.filiere.name} ({self.score})"


# ============================
# SCORE D’UNE REPONSE PAR TRAIT
# ============================

class ChoiceTraitScore(models.Model):
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name="trait_scores"
    )
    trait = models.ForeignKey(
        Trait,
        on_delete=models.CASCADE
    )
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.choice.text} → {self.trait.code} ({self.score})"


# ============================
# PROFIL RIASEC D’UNE FILIERE
# ============================

class FiliereProfile(models.Model):
    filiere = models.OneToOneField(
        Filiere,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    R = models.IntegerField(default=0)
    I = models.IntegerField(default=0)
    A = models.IntegerField(default=0)
    S = models.IntegerField(default=0)
    E = models.IntegerField(default=0)
    C = models.IntegerField(default=0)

    def __str__(self):
        return f"Profil {self.filiere.name}"


# ============================
# SESSION DE TEST
# ============================

class TestSession(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    recommended_filiere = models.ForeignKey(
        Filiere,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def can_take_test(self):
        last_test = TestSession.objects.filter(
            student=self.student,
            completed=True
        ).order_by('-started_at').first()

        if not last_test:
            return True

        return timezone.now() - last_test.started_at > timedelta(hours=24)

    def __str__(self):
        return f"Test - {self.student.username} - {self.started_at}"


# ============================
# REPONSES DE L’ETUDIANT
# ============================

class StudentAnswer(models.Model):
    test_session = models.ForeignKey(
        TestSession,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.test_session.student.username} - {self.question.id}"

# ==========================================
# STOCKAGE DES RESULTATS DE L’ETUDIANT
# ==========================================

class OrientationResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    recommended_filiere = models.ForeignKey(
        Filiere,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    score_details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.recommended_filiere}"

