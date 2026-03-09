# tests_orientation/management/commands/populate_choice_trait_scores_logic.py

from django.core.management.base import BaseCommand
from tests_orientation.models import Question, Choice, Trait, ChoiceTraitScore
from universities.models import Filiere

class Command(BaseCommand):
    help = "Remplit ChoiceTraitScore automatiquement selon la logique RIASEC par filière"

    # Définir la logique par filière (modifiable selon ton besoin)
    FILIERE_TRAIT_LOGIC = {
        "Médecine": {"R": 3, "I": 2, "S": 3, "E": 1, "A": 1, "C": 0},
        "Informatique": {"R": 2, "I": 3, "S": 1, "E": 1, "A": 1, "C": 0},
        "Droit": {"R": 1, "I": 2, "S": 1, "E": 3, "A": 0, "C": 2},
        "Finance": {"R": 1, "I": 3, "S": 0, "E": 2, "A": 0, "C": 3},
        "Marketing": {"R": 1, "I": 2, "S": 2, "E": 3, "A": 1, "C": 2},
        "Enseignement": {"R": 1, "I": 2, "S": 3, "E": 2, "A": 1, "C": 1},
        "Journalisme": {"R": 1, "I": 2, "S": 2, "E": 3, "A": 2, "C": 1},
        "Vétérinaire": {"R": 3, "I": 2, "S": 2, "E": 1, "A": 1, "C": 0},
    }

    def handle(self, *args, **options):
        traits = {t.code: t for t in Trait.objects.all()}
        questions = Question.objects.prefetch_related('choices').all()
        filieres = Filiere.objects.all()

        count = 0

        for question in questions:
            for choice in question.choices.all():
                for filiere in filieres:
                    logic = self.FILIERE_TRAIT_LOGIC.get(filiere.name)
                    if not logic:
                        continue  # Filieres sans logique définie

                    for trait_code, score in logic.items():
                        trait = traits.get(trait_code)
                        if not trait:
                            continue

                        # On ne crée que si ça n'existe pas
                        obj, created = ChoiceTraitScore.objects.get_or_create(
                            choice=choice,
                            trait=trait,
                            defaults={'score': score}
                        )
                        if created:
                            count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ChoiceTraitScore créés avec la logique RIASEC."))

