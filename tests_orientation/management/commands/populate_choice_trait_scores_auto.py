# tests_orientation/management/commands/populate_choice_trait_scores_auto.py

from django.core.management.base import BaseCommand
from tests_orientation.models import Question, Choice, Trait, ChoiceTraitScore
from universities.models import Filiere


class Command(BaseCommand):
    help = "Remplit ChoiceTraitScore automatiquement pour toutes les filières existantes."

    # Mapping automatique par première lettre
    DEFAULT_LOGIC = {
        'M': ['R', 'S'],
        'I': ['I', 'R'],
        'D': ['E', 'I'],
        'F': ['I', 'C'],
        'E': ['S', 'E'],
        'J': ['E', 'A'],
        'V': ['R', 'S']
    }

    def handle(self, *args, **options):
        traits = {t.code: t for t in Trait.objects.all()}
        questions = Question.objects.prefetch_related('choices').all()
        filieres = Filiere.objects.all()

        created_count = 0

        for question in questions:
            for choice in question.choices.all():
                for filiere in filieres:
                    # Détecte la logique selon la première lettre
                    first_letter = filiere.name[0].upper()
                    main_traits = self.DEFAULT_LOGIC.get(first_letter, [])

                    # On applique score 3 aux traits principaux, 1 aux autres
                    for code, trait in traits.items():
                        score = 3 if code in main_traits else 1
                        obj, created = ChoiceTraitScore.objects.get_or_create(
                            choice=choice,
                            trait=trait,
                            defaults={'score': score}
                        )
                        if created:
                            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created_count} ChoiceTraitScore créés automatiquement pour toutes les filières."
        ))

