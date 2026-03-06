# users/views.py

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser, AdvisorStudentRelation
from .serializers import (
    RegisterStudentSerializer,
    UserSerializer,
    AdvisorStudentRelationSerializer, AdvisorStudentStudentSerializer, chatMessageSerializer
)
from .permissions import IsStudent, IsAdvisor

from universities.models import Notification, ActionHistory

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# =====================================================
# AUTH
# =====================================================

class RegisterStudentView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterStudentSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# =====================================================
# STUDENT → SEND REQUEST
# =====================================================

class AdvisorListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(role="advisor")

class SendAdvisorRequestView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, advisor_id):

        existing_accepted = AdvisorStudentRelation.objects.filter(
            student=request.user,
            status="accepted"
        ).exists()

        if existing_accepted:
            return Response(
                {"error": "You already have an accepted advisor"},
                status=400
            )

        try:
            advisor = CustomUser.objects.get(id=advisor_id, role="advisor")
        except CustomUser.DoesNotExist:
            return Response({"error": "Advisor not found"}, status=404)

        relation, created = AdvisorStudentRelation.objects.get_or_create(
            student=request.user,
            advisor=advisor,
            defaults={"status": "pending"}
        )

        if not created:
            return Response({"error": "Request already sent"}, status=400)

        # Notification conseiller
        Notification.objects.create(
            recipient=advisor,
            message=f"Nouvelle demande de conseiller de {request.user.username}"
        )

        # Historique étudiant
        ActionHistory.objects.create(
            user=request.user,
            action_type="advisor_request",
            description=f"Demande envoyée à {advisor.username}"
        )

        return Response({"message": "Request sent"}, status=201)


# =====================================================
# ADVISOR → LIST PENDING
# =====================================================

class AdvisorRequestsView(generics.ListAPIView):
    serializer_class = AdvisorStudentRelationSerializer
    permission_classes = [IsAdvisor]

    def get_queryset(self):
        return AdvisorStudentRelation.objects.select_related(
            "student"
        ).filter(
            advisor=self.request.user,
            status="pending"
        )


# =====================================================
# ADVISOR → REVIEW
# =====================================================

class ReviewAdvisorRequestView(APIView):
    permission_classes = [IsAdvisor]

    @transaction.atomic
    def post(self, request, relation_id):

        try:
            relation = AdvisorStudentRelation.objects.select_for_update().get(
                id=relation_id,
                advisor=request.user
            )
        except AdvisorStudentRelation.DoesNotExist:
            return Response({"error": "Request not found"}, status=404)

        action = request.data.get("action")

        if action not in ["accept", "reject"]:
            return Response({"error": "Invalid action"}, status=400)

        if action == "accept":

            existing = AdvisorStudentRelation.objects.filter(
                student=relation.student,
                status="accepted"
            ).exclude(id=relation.id)

            if existing.exists():
                return Response(
                    {"error": "Student already has an accepted advisor"},
                    status=400
                )

            relation.status = "accepted"

        else:
            relation.status = "rejected"

        relation.save()

        # Notification étudiant
        Notification.objects.create(
            recipient=relation.student,
            message=f"Votre demande de conseiller a été {relation.status}"
        )

        # Historique conseiller
        ActionHistory.objects.create(
            user=request.user,
            action_type="review_advisor",
            description=f"{relation.status} la demande de {relation.student.username}"
        )

        # Historique étudiant
        ActionHistory.objects.create(
            user=relation.student,
            action_type="review_advisor",
            description=f"Votre demande a été {relation.status}"
        )

        return Response({"message": f"Request {relation.status}"})


# =====================================================
# ADVISOR → LIST STUDENTS
# =====================================================

class AdvisorStudentsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdvisor]

    def get_queryset(self):
        students_ids = AdvisorStudentRelation.objects.filter(
            advisor=self.request.user,
            status="accepted"
        ).values_list("student_id", flat=True)

        return CustomUser.objects.filter(id__in=students_ids)

# =====================================================
# Conseiller voir ses etudiants
# =====================================================
class MyStudentsListView(generics.ListAPIView):
    serializer_class = AdvisorStudentStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != "advisor":
            return CustomUser.objects.none()

        relations = AdvisorStudentRelation.objects.filter(
            advisor=user,
            status="accepted"
        )

        student_ids = relations.values_list("student_id", flat=True)

        return CustomUser.objects.filter(id__in=student_ids)


# ============== mon conseiller personnel ====================

class MyAdvisorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "student":
            return Response({"error": "Unauthorized"}, status=403)

        relation = AdvisorStudentRelation.objects.filter(
            student=user,
            status="accepted"
        ).first()

        if not relation or not relation.advisor:
            return Response({"advisor": None})

        serializer = UserSerializer(relation.advisor)
        return Response(serializer.data)

# =============== Message ====================
class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, relation_id):

        try:
            relation = AdvisorStudentRelation.objects.get(
                id=relation_id,
                status="accepted"
            )
        except AdvisorStudentRelation.DoesNotExist:
            return Response({"error": "chat not allowed"}, status=403)

        # verifier que l'utilisateur appartient a la relation'
        if request.user not in [relation.student, relation.advisor]:
            return Response({"error": "Unauthorized"}, status=401)

        messages = relation.messages.all().order_by("-created_at")
        serializer = chatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, relation_id):

        try:
            relation = AdvisorStudentRelation.objects.get(
                id=relation_id,
                status="accepted"
            )
        except AdvisorStudentRelation.DoesNotExist:
            return Response({"error": "chat not allowed"}, status=403)

        if request.user not in [relation.student, relation.advisor]:
            return Response({"error": "Unauthorized"}, status=403)

        serializer = chatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                sender=request.user,
                relation=relation,
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


