# tests_orientation/management/commands/populate_choice_trait_scores.py

from django.core.management.base import BaseCommand
from tests_orientation.models import Question, Choice, Trait, ChoiceTraitScore

import random

class Command(BaseCommand):
    help = "Remplit automatiquement les ChoiceTraitScore pour toutes les questions et traits"

    def handle(self, *args, **options):
        traits = Trait.objects.all()
        if not traits:
            self.stdout.write(self.style.ERROR("Aucun trait RIASEC trouvé !"))
            return

        questions = Question.objects.prefetch_related('choices').all()
        if not questions:
            self.stdout.write(self.style.ERROR("Aucune question trouvée !"))
            return

        count = 0
        for question in questions:
            for choice in question.choices.all():
                for trait in traits:
                    # Vérifie si le score existe déjà
                    score_obj, created = ChoiceTraitScore.objects.get_or_create(
                        choice=choice,
                        trait=trait,
                        defaults={'score': random.randint(0, 3)}  # Valeur aléatoire 0-3
                    )
                    if created:
                        count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ChoiceTraitScore ont été créés avec succès."))

