# documents/views.py
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document
from documents.serializers import DocumentSerializer
from notifications.models import Notification
from users.models import AdvisorStudentRelation


class IsStudent(BasePermission):
    def has_object_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"

class IsAdvisor(BasePermission):
    def has_object_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "advisor"

class IsUniversityStaff(BasePermission):
    def has_object_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "university-staff"

# ==============================================
# 1️Upload document (étudiant)
# ==============================================

class UploadDocumentView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==============================================
# 2️⃣ Liste documents de l’étudiant
# ==============================================

class StudentDocumentsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        documents = Document.objects.filter(student=request.user).order_by("-created_at")
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

# ==============================================
# 3️⃣ Liste documents pour le conseiller
# ==============================================

class AdvisorDocumentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "advisor":
            return Response({"error": "Unauthorized"}, status=403)

        accepted_students = AdvisorStudentRelation.objects.filter(
            advisor=request.user,
            status="accepted"
        ).values_list("student_id", flat=True)

        documents = Document.objects.filter(
            student__id__in=accepted_students
        ).order_by("-created_at")

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

# ==============================================
# 4️⃣ Valider / Rejeter un document (conseiller)
# ==============================================

class ReviewDocumentView(APIView):
    permission_classes = [IsAdvisor]

    def post(self, request, document_id):
        action = request.data.get("action")  # "validate" ou "reject"
        comment = request.data.get("comment", "")

        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document inexistant"}, status=404)

        if action not in ["validate", "reject"]:
            return Response({"error": "Action invalide"}, status=400)

        document.status = "validated" if action == "validate" else "rejected"
        document.advisor = request.user
        document.comment = comment
        document.save()

        Notification.objects.create(
            recipient=document.student,
            title=f"Document {document.get_document_type_display()} {document.status}",
            message=f"Votre document '{document.get_document_type}' a été {document.status} par {request.user.username}. Commentaire : {comment}"
        )

        serializer = DocumentSerializer(document)
        return Response(serializer.data)

