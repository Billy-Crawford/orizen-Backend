# tests_orientation/management/commands/seed_orientation_test.py

from django.core.management.base import BaseCommand
from tests_orientation.models import Question, Choice, ChoiceTraitScore
from universities.models import Filiere, University
from users.models import CustomUser


class Command(BaseCommand):
    help = "Seed complete psychological orientation test (20 questions)"

    def handle(self, *args, **kwargs):

        self.stdout.write("Cleaning old questions...")
        Question.objects.all().delete()

        # =====================================================
        # CREATION UNIVERSITE SYSTEME
        # =====================================================

        admin_user = CustomUser.objects.filter(role="admin").first()

        system_university, _ = University.objects.get_or_create(
            name="Orizen Orientation System",
            defaults={
                "description": "Filières globales pour le test d’orientation",
                "contact_email": "system@orizen.com",
                "created_by": admin_user
            }
        )

        # =====================================================
        # FILIERES
        # =====================================================

        filiere_names = [
            "Médecine",
            "Informatique",
            "Droit",
            "Journalisme",
            "Génie Civil",
            "Pétrole et Gaz",
            "Enseignement",
            "Agronomie",
            "Finance",
            "Marketing",
            "Psychologie",
            "Architecture",
            "Vétérinaire",
            "Relations Internationales",
            "Entrepreneuriat",
        ]

        filieres = {}

        for name in filiere_names:
            filiere, _ = Filiere.objects.get_or_create(
                university=system_university,
                name=name,
                defaults={"description": f"Filière {name}"}
            )
            filieres[name] = filiere

        # =====================================================
        # QUESTIONS (20)
        # =====================================================

        questions_data = [
            {
                "text": "Quand vous résolvez un problème, vous préférez :",
                "choices": {
                    "Analyser logiquement chaque détail": "Informatique",
                    "Discuter avec les personnes concernées": "Psychologie",
                    "Prendre une décision juridique claire": "Droit",
                    "Imaginer une solution innovante": "Entrepreneuriat",
                }
            },
            {
                "text": "Quel environnement vous attire le plus ?",
                "choices": {
                    "Un hôpital ou centre médical": "Médecine",
                    "Un bureau d’ingénierie ou chantier": "Génie Civil",
                    "Une salle de rédaction": "Journalisme",
                    "Une ferme ou exploitation agricole": "Agronomie",
                }
            },
            {
                "text": "Vous êtes plus motivé par :",
                "choices": {
                    "Aider les malades": "Médecine",
                    "Construire des infrastructures": "Génie Civil",
                    "Défendre les droits des autres": "Droit",
                    "Créer votre propre entreprise": "Entrepreneuriat",
                }
            },
            {
                "text": "Vous préférez travailler :",
                "choices": {
                    "Avec des chiffres": "Finance",
                    "Avec des technologies modernes": "Informatique",
                    "Avec des animaux": "Vétérinaire",
                    "Avec des étudiants": "Enseignement",
                }
            },
            {
                "text": "Dans un projet d’équipe, vous êtes souvent :",
                "choices": {
                    "Le leader stratégique": "Entrepreneuriat",
                    "L’analyste technique": "Informatique",
                    "Le médiateur": "Psychologie",
                    "Le créatif": "Marketing",
                }
            },
            {
                "text": "Quel sujet vous passionne le plus ?",
                "choices": {
                    "Le corps humain": "Médecine",
                    "Les lois et la justice": "Droit",
                    "Les marchés financiers": "Finance",
                    "Les relations entre pays": "Relations Internationales",
                }
            },
            {
                "text": "Vous préférez un métier :",
                "choices": {
                    "Stable et réglementé": "Droit",
                    "Technique et évolutif": "Informatique",
                    "Créatif et artistique": "Architecture",
                    "Lié aux ressources énergétiques": "Pétrole et Gaz",
                }
            },
            {
                "text": "Vous aimez davantage :",
                "choices": {
                    "Soigner les animaux": "Vétérinaire",
                    "Former la nouvelle génération": "Enseignement",
                    "Informer le public": "Journalisme",
                    "Développer une stratégie commerciale": "Marketing",
                }
            },
            {
                "text": "Face à un défi complexe, vous :",
                "choices": {
                    "Cherchez une solution scientifique": "Médecine",
                    "Construisez un modèle technique": "Génie Civil",
                    "Analysez les impacts économiques": "Finance",
                    "Étudiez l’impact social": "Psychologie",
                }
            },
            {
                "text": "Vous vous imaginez travailler :",
                "choices": {
                    "À l’international": "Relations Internationales",
                    "Dans une startup": "Entrepreneuriat",
                    "Dans une grande entreprise technologique": "Informatique",
                    "Dans une organisation agricole": "Agronomie",
                }
            },
            {
                "text": "Vous préférez résoudre des problèmes :",
                "choices": {
                    "Techniques": "Informatique",
                    "Humains": "Psychologie",
                    "Juridiques": "Droit",
                    "Financiers": "Finance",
                }
            },
            {
                "text": "Quel rôle vous correspond le plus ?",
                "choices": {
                    "Architecte d’un bâtiment": "Architecture",
                    "Médecin spécialiste": "Médecine",
                    "Journaliste d’investigation": "Journalisme",
                    "Ingénieur pétrolier": "Pétrole et Gaz",
                }
            },
            {
                "text": "Vous aimez travailler :",
                "choices": {
                    "En laboratoire": "Médecine",
                    "Sur le terrain agricole": "Agronomie",
                    "Sur un chantier": "Génie Civil",
                    "Devant un ordinateur": "Informatique",
                }
            },
            {
                "text": "Votre plus grande qualité est :",
                "choices": {
                    "Empathie": "Psychologie",
                    "Logique": "Informatique",
                    "Charisme": "Marketing",
                    "Rigueur": "Finance",
                }
            },
            {
                "text": "Vous préférez un impact :",
                "choices": {
                    "Sanitaire": "Médecine",
                    "Économique": "Finance",
                    "Social": "Psychologie",
                    "Médiatique": "Journalisme",
                }
            },
            {
                "text": "Vous êtes attiré par :",
                "choices": {
                    "Les tribunaux": "Droit",
                    "Les hôpitaux vétérinaires": "Vétérinaire",
                    "Les écoles": "Enseignement",
                    "Les entreprises internationales": "Relations Internationales",
                }
            },
            {
                "text": "Vous aimez concevoir :",
                "choices": {
                    "Des bâtiments": "Architecture",
                    "Des logiciels": "Informatique",
                    "Des campagnes marketing": "Marketing",
                    "Des plans financiers": "Finance",
                }
            },
            {
                "text": "Vous préférez analyser :",
                "choices": {
                    "Des lois": "Droit",
                    "Des données médicales": "Médecine",
                    "Des statistiques économiques": "Finance",
                    "Des comportements humains": "Psychologie",
                }
            },
            {
                "text": "Vous aimeriez contribuer à :",
                "choices": {
                    "La santé publique": "Médecine",
                    "Le développement technologique": "Informatique",
                    "La justice sociale": "Droit",
                    "Le développement agricole": "Agronomie",
                }
            },
            {
                "text": "Votre ambition principale est :",
                "choices": {
                    "Sauver des vies": "Médecine",
                    "Créer une entreprise prospère": "Entrepreneuriat",
                    "Informer le monde": "Journalisme",
                    "Construire des infrastructures durables": "Génie Civil",
                }
            },
        ]

        for q_data in questions_data:
            question = Question.objects.create(text=q_data["text"])

            for choice_text, filiere_name in q_data["choices"].items():
                choice = Choice.objects.create(
                    question=question,
                    text=choice_text
                )

                ChoiceTraitScore.objects.create(
                    choice=choice,
                    filiere=filieres[filiere_name],
                    score=5
                )

        self.stdout.write(self.style.SUCCESS("✅ 20 questions seeded successfully"))

