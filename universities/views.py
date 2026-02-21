# universities/views.py

from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import University, Filiere, Candidature
from .serializers import UniversitySerializer, FiliereSerializer, FiliereCreateSerializer, CandidatureSerializer, CandidatureCreateSerializer

# Universités - CRUD pour admin
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
    permission_classes = [permissions.IsAdminUser]

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

        # 1️⃣ Vérifier rôle
        if user.role != "university":
            raise PermissionDenied("Seuls les universités peuvent accepter/rejeter.")

        # 2️⃣ Vérifier que la candidature concerne cette université
        if candidature.filiere.university.created_by != user:
            raise PermissionDenied("Cette candidature ne concerne pas votre université.")

        # 3️⃣ Mettre à jour le statut
        status_value = request.data.get("status")
        if status_value not in ["accepted", "rejected"]:
            return Response(
                {"error": "Le statut doit être 'accepted' ou 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        candidature.status = status_value
        candidature.reviewed_by = user
        candidature.save()

        serializer = self.get_serializer(candidature)
        return Response(serializer.data)
