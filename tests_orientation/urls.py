# tests_orientation/urls.py

from django.urls import path
from .views import StartTestView, TestQuestionsView, SubmitAnswerView, TestResultView, StudentOrientationHistoryView

urlpatterns = [
    path("start/", StartTestView.as_view()),
    path("<int:session_id>/questions/", TestQuestionsView.as_view()),
    path("<int:session_id>/answer/", SubmitAnswerView.as_view()),
    path("<int:session_id>/result/", TestResultView.as_view()),
    path("history/", StudentOrientationHistoryView.as_view()),
]