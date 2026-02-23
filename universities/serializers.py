# universities/serializers.py
from django.db import transaction
from rest_framework import serializers
from .models import University, Filiere, Candidature, Notification, ActionHistory
from users.serializers import UserSerializer
from users.models import CustomUser
from django.contrib.auth.hashers import make_password


class UniversityAdminCreateSerializer(serializers.Serializer):
    # User
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # University
    name = serializers.CharField()
    description = serializers.CharField()
    contact_email = serializers.EmailField()

    # ✅ Username unique
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce username existe déjà.")
        return value

    # ✅ Email unique
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email existe déjà.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            role="university"
        )

        university = University.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            contact_email=validated_data['contact_email'],
            created_by=user
        )

        return university

    # ✅ IMPORTANT : dire comment représenter la réponse
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "description": instance.description,
            "contact_email": instance.contact_email,
            "username": instance.created_by.username,
            "email": instance.created_by.email,
        }


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'description', 'logo', 'contact_email']

class FiliereSerializer(serializers.ModelSerializer):
    university = UniversitySerializer(read_only=True)

    class Meta:
        model = Filiere
        fields = ['id', 'name', 'description', 'university']

class FiliereCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filiere
        fields = ['id', 'name', 'description', 'university']

class CandidatureSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    filiere = FiliereSerializer(read_only=True)

    class Meta:
        model = Candidature
        fields = ['id', 'student', 'filiere', 'status', 'submitted_at', 'reviewed_by']


class CandidatureCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidature
        fields = ['filiere']

    def validate(self, data):
        request = self.context['request']
        user = request.user
        filiere = data['filiere']

        # 1️⃣ Vérifier rôle
        if user.role != 'student':
            raise serializers.ValidationError("Seuls les étudiants peuvent postuler.")

        # 2️⃣ Vérifier doublon
        if Candidature.objects.filter(student=user, filiere=filiere).exists():
            raise serializers.ValidationError("Vous avez déjà postulé à cette filière.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return Candidature.objects.create(
            student=user,
            filiere=validated_data['filiere'],
            status='pending'
        )

# Notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "created_at", "is_read"]

# Historique
class ActionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionHistory
        fields = ["id", "action_type", "description", "created_at"]