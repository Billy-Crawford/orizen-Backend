# users/urls.py

from django.urls import path
from .views import RegisterStudentView, UserProfileView, MyTokenObtainPairView, ReviewAdvisorRequestView, \
    SendAdvisorRequestView, AdvisorStudentsView, AdvisorRequestsView, AdvisorListView, MyStudentsListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterStudentView.as_view(), name='student-register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path("advisor/request/<int:advisor_id>/", SendAdvisorRequestView.as_view()),
    path("advisor/review/<int:relation_id>/", ReviewAdvisorRequestView.as_view()),
    path("advisor/students/", AdvisorStudentsView.as_view()),

    # demandes/conseillers
    path('send-request/<int:advisor_id>/', SendAdvisorRequestView.as_view(), name='send-request'),
    path('advisor-requests/', AdvisorRequestsView.as_view(), name='advisor-requests'),
    path('review-request/<int:relation_id>/', ReviewAdvisorRequestView.as_view(), name='review-request'),
    path('advisor-students/', AdvisorStudentsView.as_view(), name='advisor-students'),

    # ✅ Liste de tous les conseillers
    path('advisors/', AdvisorListView.as_view(), name='advisor-list'),

    # conseiller voit ses etudiant
    path("my-students/", MyStudentsListView.as_view()),
]
