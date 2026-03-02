# documents/serializers.py
from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    filiere_name = serializers.CharField(source="filiere.name", read_only=True)
    advisor_username = serializers.CharField(source="advisor.username", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "student",
            "student_username",
            "filiere",
            "filiere_name",
            "document_type",
            "file",
            "status",
            "advisor",
            "advisor_username",
            "comment",
            "created_at",
        ]
        read_only_fields = ["student", "status", "advisor", "comment", "created_at"]


