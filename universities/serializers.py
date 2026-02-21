# universities/serializers.py

from rest_framework import serializers
from .models import University, Filiere, Candidature
from users.serializers import UserSerializer

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