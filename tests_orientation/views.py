# tests_orientation/views.py

from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import random

from .models import (
    TestSession,
    Question,
    StudentAnswer,
    ChoiceTraitScore,
    OrientationResult,
    Trait,
    FiliereProfile
)

from .serializer import QuestionSerializer, OrientationResultSerializer
from universities.models import Filiere


# ==================================================
#                   PERMISSION
# ==================================================

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsUniversityStaff(BasePermission):
    """Autoriser uniquement les utilisateurs rattachés à une université"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "university_staff"


class UniversityOrientationResultsView(APIView):
    permission_classes = [IsUniversityStaff]

    def get(self, request):
        university = request.user.university  # supposition : user lié à une université

        # On récupère toutes les filières de l'université
        filieres_ids = university.filieres.values_list("id", flat=True)

        # On filtre tous les résultats d'orientation pour ces filières
        results = OrientationResult.objects.filter(recommended_filiere__id__in=filieres_ids).order_by("-created_at")

        serializer = OrientationResultSerializer(results, many=True)
        return Response(serializer.data)


# ==================================================
#                   START TEST
# ==================================================

class StartTestView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        session = TestSession(student=request.user)

        if not session.can_take_test():
            return Response(
                {"error": "Vous devez attendre 24h avant de repasser le test."},
                status=400
            )

        session.save()

        return Response({
            "message": "Test démarré",
            "session_id": session.id
        })


# ==================================================
#           GET QUESTIONS (5 PAR PAGE)
# ==================================================

class TestQuestionsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, session_id):
        page = int(request.GET.get("page", 1))

        try:
            session = TestSession.objects.get(id=session_id, student=request.user)
        except TestSession.DoesNotExist:
            return Response({"error": "Session invalide"}, status=404)

        questions = list(Question.objects.all())
        random.shuffle(questions)

        start = (page - 1) * 5
        end = start + 5

        serializer = QuestionSerializer(questions[start:end], many=True)
        return Response(serializer.data)


# ==================================================
#                   SUBMIT ANSWER
# ==================================================

class SubmitAnswerView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, session_id):
        question_id = request.data.get("question")
        choice_id = request.data.get("selected_choice")

        if not question_id or not choice_id:
            return Response({"error": "Données invalides"}, status=400)

        try:
            session = TestSession.objects.get(id=session_id, student=request.user)
        except TestSession.DoesNotExist:
            return Response({"error": "Session invalide"}, status=404)

        StudentAnswer.objects.update_or_create(
            test_session=session,
            question_id=question_id,
            defaults={"selected_choice_id": choice_id}
        )

        return Response({"message": "Réponse enregistrée"})


class StudentRiasecScoresView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, student_id=None):
        # si student_id n'est pas fourni, prend l'utilisateur courant
        student_id = student_id or request.user.id
        results = OrientationResult.objects.filter(student_id=student_id).order_by("-created_at")
        data = [
            {
                "filiere": r.recommended_filiere.name,
                "scores": r.score_details
            }
            for r in results
        ]
        return Response(data)


# ==================================================
#                   CALCUL DU RESULTAT
# ==================================================

class TestResultView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, session_id):

        try:
            session = TestSession.objects.get(id=session_id, student=request.user)
        except TestSession.DoesNotExist:
            return Response({"error": "Session invalide"}, status=404)

        if session.completed:
            return Response({
                "recommended_filiere": session.recommended_filiere.name
            })

        answers = session.answers.all()

        if not answers.exists():
            return Response({"error": "Aucune réponse trouvée"}, status=400)

        # ==============================
        # 1️⃣ Calcul profil RIASEC étudiant
        # ==============================

        trait_scores = {
            "R": 0,
            "I": 0,
            "A": 0,
            "S": 0,
            "E": 0,
            "C": 0,
        }

        for answer in answers:
            scores = ChoiceTraitScore.objects.filter(
                choice=answer.selected_choice
            )

            for s in scores:
                trait_scores[s.trait.code] += s.score

        # ===================================================
        # 2     ️Comparaison avec profils filières
        # ===================================================

        compatibility_results = []

        for profile in FiliereProfile.objects.all():
            compatibility = (
                trait_scores["R"] * profile.R +
                trait_scores["I"] * profile.I +
                trait_scores["A"] * profile.A +
                trait_scores["S"] * profile.S +
                trait_scores["E"] * profile.E +
                trait_scores["C"] * profile.C
            )

            compatibility_results.append(
                (profile.filiere.name, compatibility)
            )

        # Trier par score décroissant
        compatibility_results.sort(key=lambda x: x[1], reverse=True)

        top_3 = compatibility_results[:3]

        if not top_3:
            return Response({"error": "Aucune filière compatible trouvée"}, status=400)

        recommended_name = top_3[0][0]
        # recommended_obj = Filiere.objects.get(name=recommended_name)
        recommended_obj = Filiere.objects.filter(name=recommended_name).first()


        # ====================================================
        # 3️             Sauvegarde session
        # ====================================================

        session.recommended_filiere = recommended_obj
        session.completed = True
        session.save()

        # ====================================================
        #       4️        Sauvegarde historique
        # ====================================================

        OrientationResult.objects.create(
            student=request.user,
            recommended_filiere=recommended_obj,
            score_details={
                "student_profile": trait_scores,
                "compatibility_scores": dict(compatibility_results)
            }
        )

        # Identifier les 2 traits dominants
        sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
        top_traits = sorted_traits[:2]

        interpretation = f"Votre profil dominant est {top_traits[0][0]}-{top_traits[1][0]}."

        explanations = {
            "R": "Vous aimez les activités concrètes, pratiques et techniques.",
            "I": "Vous êtes analytique et aimez résoudre des problèmes complexes.",
            "A": "Vous êtes créatif et aimez vous exprimer.",
            "S": "Vous aimez aider et travailler avec les autres.",
            "E": "Vous aimez diriger, convaincre et entreprendre.",
            "C": "Vous êtes organisé et appréciez les environnements structurés."
        }

        interpretation += " " + explanations[top_traits[0][0]]

        return Response({
            "recommended_filiere": recommended_name,
            "top_3": top_3,
            "student_profile": trait_scores,
            "interpretation": interpretation
        })


# ===============================================================
#                   HISTORIQUE ORIENTATION
# ===============================================================

class StudentOrientationHistoryView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        results = OrientationResult.objects.filter(
            student=request.user
        ).order_by("-created_at")

        serializer = OrientationResultSerializer(results, many=True)
        return Response(serializer.data)

