# tests_orientation/admin.py

from django.contrib import admin
from .models import (
    Question,
    Choice,
    Trait,
    ChoiceTraitScore,
    FiliereProfile,
    TestSession,
    StudentAnswer,
    OrientationResult
)

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Trait)
admin.site.register(ChoiceTraitScore)
admin.site.register(FiliereProfile)
admin.site.register(TestSession)
admin.site.register(StudentAnswer)
admin.site.register(OrientationResult)

