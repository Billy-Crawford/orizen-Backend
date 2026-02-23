# universities/permissions.py
from rest_framework import permissions

class IsAdminOrUniversity(permissions.BasePermission):
    """
    Permet aux admins ou aux universités de créer des filières
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'university']