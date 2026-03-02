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
        fields = [
            'id',
            'student',
            'filiere',
            'status',
            'submitted_at',
            'advisor',
            'advisor_approved',
            'reviewed_by_university'
        ]

class CandidatureCreateSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Candidature
        fields = ['filiere', 'student_id']

    def validate(self, data):
        request = self.context['request']
        user = request.user
        filiere = data['filiere']

        # ----------------------
        # CAS ETUDIANT
        # ----------------------
        if user.role == 'student':

            if Candidature.objects.filter(student=user, filiere=filiere).exists():
                raise serializers.ValidationError(
                    "Vous avez déjà postulé à cette filière."
                )

        # ----------------------
        # CAS CONSEILLER
        # ----------------------
        elif user.role == 'advisor':

            student_id = data.get("student_id")

            if not student_id:
                raise serializers.ValidationError("student_id is required.")

            from users.models import AdvisorStudentRelation

            relation = AdvisorStudentRelation.objects.filter(
                advisor=user,
                student_id=student_id,
                status="accepted"
            ).first()

            if not relation:
                raise serializers.ValidationError(
                    "Ce student ne vous est pas assigné."
                )

            if Candidature.objects.filter(
                student=relation.student,
                filiere=filiere
            ).exists():
                raise serializers.ValidationError(
                    "Ce student a déjà postulé à cette filière."
                )

        else:
            raise serializers.ValidationError(
                "Seuls les étudiants ou conseillers peuvent postuler."
            )

        return data


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