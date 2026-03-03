# universities/views.py

from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from users.permissions import IsUniversity
from .models import University, Filiere, Candidature, Notification, ActionHistory
from .permissions import IsAdminOrUniversity
from .serializers import UniversitySerializer, FiliereSerializer, FiliereCreateSerializer, CandidatureSerializer, \
    CandidatureCreateSerializer, UniversityAdminCreateSerializer, NotificationSerializer, ActionHistorySerializer


# Universités - CRUD pour admin
class UniversityAdminCreateView(generics.CreateAPIView):
    serializer_class = UniversityAdminCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class UniversityListView(generics.ListAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAuthenticated]


class UniversityCreateView(generics.CreateAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAdminUser]


class UniversityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAdminUser]


# Filières
class FiliereListView(generics.ListAPIView):
    serializer_class = FiliereSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Filiere.objects.all()
        university_id = self.request.query_params.get('university_id')

        if university_id:
            queryset = queryset.filter(university_id=university_id)

        return queryset


class FiliereCreateView(generics.CreateAPIView):
    queryset = Filiere.objects.all()
    serializer_class = FiliereCreateSerializer
    permission_classes = [IsAdminOrUniversity]


# Candidature

class CandidatureListView(generics.ListAPIView):
    serializer_class = CandidatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Candidature.objects.all()

        if user.role == "advisor":
            # Conseiller voit uniquement les candidatures
            # de ses étudiants acceptés
            from users.models import AdvisorStudentRelation

            students_ids = AdvisorStudentRelation.objects.filter(
                advisor=user,
                status="accepted"
            ).values_list("student_id", flat=True)

            return Candidature.objects.filter(student_id__in=students_ids)

        if user.role == "student":
            return Candidature.objects.filter(student=user)

        if user.role == "university":
            return Candidature.objects.filter(
                filiere__university__created_by=user
            )

        return Candidature.objects.none()


class CandidatureCreateView(generics.CreateAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # --------------------------
        # CAS 1 : ETUDIANT
        # --------------------------
        if user.role == "student":

            from users.models import AdvisorStudentRelation

            relation = AdvisorStudentRelation.objects.filter(
                student=user,
                status="accepted"
            ).first()

            # Étudiant a un conseiller
            if relation:
                serializer.save(
                    student=user,
                    advisor=relation.advisor,
                    advisor_approved=False
                )
            else:
                # Étudiant sans conseiller
                serializer.save(
                    student=user,
                    advisor=None,
                    advisor_approved=False
                )

        # --------------------------
        # CAS 2 : CONSEILLER pousse le dossier
        # --------------------------
        elif user.role == "advisor":

            student_id = self.request.data.get("student_id")

            if not student_id:
                raise PermissionDenied("student_id is required.")

            from users.models import AdvisorStudentRelation

            relation = AdvisorStudentRelation.objects.filter(
                advisor=user,
                student_id=student_id,
                status="accepted"
            ).first()

            if not relation:
                raise PermissionDenied("This student is not assigned to you.")

            serializer.save(
                student=relation.student,
                advisor=user,
                advisor_approved=True
            )

        else:
            raise PermissionDenied("Only students or advisors can create candidatures.")


# Accept / Reject candidature
class CandidatureUpdateStatusView(generics.UpdateAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    permission_classes = [IsUniversity]

    def update(self, request, *args, **kwargs):
        candidature = self.get_object()
        user = request.user

        # Vérifier rôle
        if user.role != "university":
            raise PermissionDenied("Seuls les universités peuvent accepter/rejeter.")

        # Vérifier que la candidature appartient à son université
        if candidature.filiere.university.created_by != user:
            raise PermissionDenied("Cette candidature ne concerne pas votre université.")

        status_value = request.data.get("status")
        if status_value not in ["accepted", "rejected"]:
            return Response(
                {"error": "Le statut doit être 'accepted' ou 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mise à jour
        candidature.status = status_value
        candidature.reviewed_by_university = user
        candidature.save()

        # Notification étudiant
        message = (
            f"Votre candidature à la filière {candidature.filiere.name} "
            f"de l'université {candidature.filiere.university.name} "
            f"a été {status_value}."
        )

        Notification.objects.create(
            recipient=candidature.student,
            message=message
        )

        # Historique université
        ActionHistory.objects.create(
            user=user,
            action_type="update_status",
            description=f"A {'accepté' if status_value == 'accepted' else 'rejeté'} "
                        f"la candidature de {candidature.student.username}"
        )

        # Historique étudiant
        ActionHistory.objects.create(
            user=candidature.student,
            action_type="update_status",
            description=f"Votre candidature pour {candidature.filiere.name} "
                        f"a été {status_value}"
        )

        serializer = self.get_serializer(candidature)
        return Response(serializer.data)



# recupere notifications et historique
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")


class ActionHistoryListView(generics.ListAPIView):
    serializer_class = ActionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ActionHistory.objects.filter(user=self.request.user).order_by("-created_at")