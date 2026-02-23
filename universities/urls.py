# universities/urls.py

from django.urls import path
from .views import (
    UniversityListView,
    UniversityCreateView,
    UniversityDetailView,
    FiliereListView,
    FiliereCreateView,
    CandidatureListView,
    CandidatureCreateView,
    CandidatureUpdateStatusView,
    UniversityAdminCreateView, ActionHistoryListView, NotificationListView,
)

urlpatterns = [
    path('universities/', UniversityListView.as_view()),
    path('universities/create/', UniversityCreateView.as_view()),
    path('universities/<int:pk>/', UniversityDetailView.as_view()),
    path('admin/create-university/', UniversityAdminCreateView.as_view()),

    path('filieres/', FiliereListView.as_view()),
    path('filieres/create/', FiliereCreateView.as_view()),

    path('candidatures/', CandidatureListView.as_view()),
    path('candidatures/create/', CandidatureCreateView.as_view()),
    path('candidatures/<int:pk>/update/', CandidatureUpdateStatusView.as_view()),

    path('notifications/', NotificationListView.as_view()),
    path('history/', ActionHistoryListView.as_view()),
]
