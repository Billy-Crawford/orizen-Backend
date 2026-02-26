# tests_orientation/management/commands/seed_traits_profiles.py

from django.core.management.base import BaseCommand
from tests_orientation.models import Trait, FiliereProfile
from universities.models import Filiere


class Command(BaseCommand):
    help = "Seed RAISEC traits and filiere profiles (création ou mise à jour)"

    def handle(self, *args, **kwargs):

        # ======================
        # 1- TRAITS RIASEC
        # ======================
        traits_data = [
            ("R", "Réaliste"),
            ("I", "Investigateur"),
            ("A", "Artistique"),
            ("S", "Social"),
            ("E", "Entreprenant"),
            ("C", "Conventionnel"),
        ]

        traits = {}
        for code, name in traits_data:
            trait, created = Trait.objects.get_or_create(code=code, defaults={"name": name})
            traits[code] = trait
            if created:
                self.stdout.write(f"✅ Trait créé : {code} - {name}")
            else:
                self.stdout.write(f"⚡ Trait existant : {code} - {name}")

        # ======================
        # 2- PROFILS FILIÈRES
        # ======================
        filiere_profiles = {
            "Médecine": dict(R=2, I=5, A=1, S=5, E=2, C=3),
            "Informatique": dict(R=3, I=5, A=2, S=1, E=2, C=4),
            "Journalisme": dict(R=1, I=3, A=5, S=4, E=4, C=2),
            "Vétérinaire": dict(R=5, I=4, A=1, S=4, E=2, C=2),
            "Enseignement": dict(R=1, I=3, A=3, S=5, E=2, C=3),
            "Ingénierie civile": dict(R=5, I=4, A=1, S=1, E=3, C=4),
            "Pétrole & Gaz": dict(R=5, I=4, A=1, S=1, E=3, C=4),
            "Finance": dict(R=1, I=4, A=1, S=1, E=4, C=5),
            "Marketing": dict(R=1, I=2, A=4, S=4, E=5, C=2),
            "Droit": dict(R=1, I=4, A=2, S=3, E=4, C=4),
        }

        for filiere_name, profile in filiere_profiles.items():
            filieres = Filiere.objects.filter(name=filiere_name)
            if not filieres.exists():
                self.stdout.write(self.style.WARNING(
                    f"⚠ Filière '{filiere_name}' inexistante — ignorée"
                ))
                continue

            for filiere in filieres:
                # Créer ou mettre à jour le profil existant
                filiere_profile, created = FiliereProfile.objects.update_or_create(
                    filiere=filiere,
                    defaults={
                        "R": profile["R"],
                        "I": profile["I"],
                        "A": profile["A"],
                        "S": profile["S"],
                        "E": profile["E"],
                        "C": profile["C"],
                    }
                )
                action = "Créé" if created else "Mis à jour"
                self.stdout.write(f"✅ Profil {action} pour '{filiere_name}' ({filiere.university.name})")

        self.stdout.write(self.style.SUCCESS("🎯 Tous les profils filières ont été créés ou mis à jour avec succès"))