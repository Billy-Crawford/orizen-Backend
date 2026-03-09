# tests_orientation/management/commands/populate_choice_trait_scores_smart.py

from django.core.management.base import BaseCommand
from tests_orientation.models import Question, Choice, Trait, ChoiceTraitScore, FiliereProfile

class Command(BaseCommand):
    help = "Remplit automatiquement ChoiceTraitScore en fonction du profil RIASEC des filières."

    def handle(self, *args, **options):
        traits = {t.code: t for t in Trait.objects.all()}
        questions = Question.objects.prefetch_related('choices').all()
        profiles = FiliereProfile.objects.select_related('filiere').all()

        created_count = 0

        for profile in profiles:
            filiere = profile.filiere
            trait_scores = {
                'R': profile.R,
                'I': profile.I,
                'A': profile.A,
                'S': profile.S,
                'E': profile.E,
                'C': profile.C
            }

            for question in questions:
                for choice in question.choices.all():
                    for code, score in trait_scores.items():
                        trait = traits[code]
                        # Crée le score si il n'existe pas
                        obj, created = ChoiceTraitScore.objects.get_or_create(
                            choice=choice,
                            trait=trait,
                            defaults={'score': score}
                        )
                        if created:
                            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created_count} ChoiceTraitScore intelligents créés pour toutes les filières."
        ))

