# users/serializers.py

from rest_framework import serializers
from .models import CustomUser, AdvisorStudentRelation, chatMessage
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'phone', 'photo']

class RegisterStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='student'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AdvisorStudentRelationSerializer(serializers.ModelSerializer):
        student_username = serializers.CharField(source="student.username", read_only=True)
        advisor_username = serializers.CharField(source="advisor.username", read_only=True)

        class Meta:
            model = AdvisorStudentRelation
            fields = "__all__"


# =================== Conseiller voit ses etudiants ===================

class AdvisorStudentStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]

# =============== Message =================
class chatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = chatMessage
        fields = ["id", "sender", "sender_username", "message", "created_at"]
        read_only_fields = ["sender"]

