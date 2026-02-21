# users/views.py

from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import RegisterStudentSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Inscription étudiant
class RegisterStudentView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterStudentSerializer
    permission_classes = [permissions.AllowAny]

# Récupération profil connecté
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# JWT personnalisé pour inclure role
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajout du role dans le token
        token['role'] = user.role
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
