from django.urls import path

from .views import (
    InterviewSessionGenerateAPIView,
    InterviewSessionListCreateAPIView,
    InterviewSessionRetrieveAPIView,
)

urlpatterns = [
    path("interviews/sessions/", InterviewSessionListCreateAPIView.as_view(), name="ai-interview-session-list"),
    path(
        "interviews/sessions/generate/",
        InterviewSessionGenerateAPIView.as_view(),
        name="ai-interview-session-generate",
    ),
    path(
        "interviews/sessions/<uuid:id>/",
        InterviewSessionRetrieveAPIView.as_view(),
        name="ai-interview-session-detail",
    ),
]
