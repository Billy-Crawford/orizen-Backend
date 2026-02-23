# tests_orientation/models.py
from django.db import models
from users.models import CustomUser
from universities.models import Filiere

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    filiere_category = models.CharField(max_length=50)  # ex: "Science", "Informatique", "Gestion"
    score_value = models.IntegerField(default=1)        # points attribués à cette catégorie

    def __str__(self):
        return f"{self.text} ({self.filiere_category})"

class ReponseEtudiant(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.question.id} : {self.option.text}"

