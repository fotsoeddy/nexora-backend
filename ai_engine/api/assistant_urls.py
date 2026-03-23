from django.urls import path

from .chat_views import (
    ChatMessageCreateAPIView,
    ChatSessionListCreateAPIView,
    ChatSessionRetrieveAPIView,
)
from .cover_letter_views import CoverLetterGenerateAPIView
from .salary_views import SalaryEstimateCreateAPIView
from .views import InterviewAnswerSubmitAPIView

urlpatterns = [
    path("cover-letters/generate/", CoverLetterGenerateAPIView.as_view(), name="ai-cover-letter-generate"),
    path("salary-estimates/", SalaryEstimateCreateAPIView.as_view(), name="ai-salary-estimate-create"),
    path(
        "interviews/sessions/<uuid:id>/answers/",
        InterviewAnswerSubmitAPIView.as_view(),
        name="ai-interview-answer-submit",
    ),
    path("chat/sessions/", ChatSessionListCreateAPIView.as_view(), name="ai-chat-session-list"),
    path("chat/sessions/<uuid:id>/", ChatSessionRetrieveAPIView.as_view(), name="ai-chat-session-detail"),
    path("chat/sessions/<uuid:id>/messages/", ChatMessageCreateAPIView.as_view(), name="ai-chat-message-create"),
]
