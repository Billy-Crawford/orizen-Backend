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