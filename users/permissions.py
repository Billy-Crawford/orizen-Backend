# users/permissions.py
from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"

class IsAdvisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "advisor"

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

# class IsAdvisor(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == "advisor"

class IsUniversity(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "university"

# class IsStudent(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == "student"

