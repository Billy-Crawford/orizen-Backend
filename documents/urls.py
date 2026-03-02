# documents/urls.oy

from django.urls import path
from .views import (
    UploadDocumentView,
    StudentDocumentsView,
    AdvisorDocumentsView,
    ReviewDocumentView
)

urlpatterns = [
    path("upload/", UploadDocumentView.as_view(), name="upload_document"),
    path("student/", StudentDocumentsView.as_view(), name="student_documents"),
    path("advisor/", AdvisorDocumentsView.as_view(), name="advisor_documents"),
    path("review/<int:document_id>/", ReviewDocumentView.as_view(), name="review_document"),
]