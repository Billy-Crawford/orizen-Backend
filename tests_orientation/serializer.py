# tests_orientation/serializers.py
from rest_framework import serializers
from .models import Question, Choice, TestSession, StudentAnswer, OrientationResult


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "choices"]


class TestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = ["id", "started_at", "completed", "recommended_filiere"]


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ["question", "selected_choice"]


class OrientationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrientationResult
        fields = ['__all__']


class OrientationHistorySerializer(serializers.ModelSerializer):
    recommended_filiere = serializers.SerializerMethodField()
    top_3 = serializers.SerializerMethodField()
    student_profile = serializers.SerializerMethodField()
    interpretation = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source="created_at")

    class Meta:
        model = OrientationResult
        fields = ["id", "recommended_filiere", "top_3", "student_profile", "interpretation", "date"]

    def get_recommended_filiere(self, obj):
        return obj.recommended_filiere.name if obj.recommended_filiere else None

    def get_top_3(self, obj):
        if obj.score_details and "top_3" in obj.score_details:
            return obj.score_details["top_3"]
        return []

    def get_student_profile(self, obj):
        if obj.score_details and "student_profile" in obj.score_details:
            return obj.score_details["student_profile"]
        return {}

    def get_interpretation(self, obj):
        if obj.score_details and "interpretation" in obj.score_details:
            return obj.score_details["interpretation"]
        return None

