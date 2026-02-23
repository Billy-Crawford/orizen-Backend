# universities/views.py

from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

        # Admin voit tout
        if user.role == "admin":
            return Candidature.objects.all()

        # Conseiller voit tout (V1)
        if user.role == "advisor":
            return Candidature.objects.all()

        # Étudiant voit ses candidatures
        if user.role == "student":
            return Candidature.objects.filter(student=user)

        # Université voit candidatures liées à ses filières
        if user.role == "university":
            return Candidature.objects.filter(
                filiere__university__created_by=user
            )

        return Candidature.objects.none()


class CandidatureCreateView(generics.CreateAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


# Accept / Reject candidature
class CandidatureUpdateStatusView(generics.UpdateAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        candidature = self.get_object()
        user = request.user

        if user.role != "university":
            raise PermissionDenied("Seuls les universités peuvent accepter/rejeter.")

        if candidature.filiere.university.created_by != user:
            raise PermissionDenied("Cette candidature ne concerne pas votre université.")

        status_value = request.data.get("status")
        if status_value not in ["accepted", "rejected"]:
            return Response(
                {"error": "Le statut doit être 'accepted' ou 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mettre à jour le statut
        candidature.status = status_value
        candidature.reviewed_by = user
        candidature.save()

        # --- 1️⃣ Notification à l'étudiant ---
        message = f"Votre candidature à la filière {candidature.filiere.name} de l'université {candidature.filiere.university.name} a été {status_value}."
        Notification.objects.create(recipient=candidature.student, message=message)

        # --- 2️⃣ Historique pour les 3 utilisateurs ---
        ActionHistory.objects.create(
            user=user,
            action_type="update_status",
            description=f"A {'accepté' if status_value=='accepted' else 'rejetté'} la candidature de {candidature.student.username} pour {candidature.filiere.name}"
        )

        # Historique pour l'étudiant
        ActionHistory.objects.create(
            user=candidature.student,
            action_type="update_status",
            description=f"Votre candidature pour {candidature.filiere.name} a été {status_value} par {user.username}"
        )

        # Historique pour l'admin (on prend le premier admin pour l'exemple)
        from users.models import CustomUser
        admin_user = CustomUser.objects.filter(role="admin").first()
        if admin_user:
            ActionHistory.objects.create(
                user=admin_user,
                action_type="update_status",
                description=f"{user.username} a {'accepté' if status_value=='accepted' else 'rejetté'} la candidature de {candidature.student.username}"
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