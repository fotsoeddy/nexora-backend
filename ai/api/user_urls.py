from django.urls import path

from ai.api.views.application import ApplicationListCreateAPIView
from ai.api.views.assistant import (
    ChatMessageCreateAPIView,
    ChatSessionListCreateAPIView,
    ChatSessionRetrieveAPIView,
    CoverLetterGenerateAPIView,
    SalaryEstimateCreateAPIView,
)
from ai.api.views.interview import InterviewAnswerSubmitView
from ai.api.views.job_alert import JobAlertListCreateAPIView, JobAlertRetrieveUpdateAPIView
from ai.api.views.saved_job import SavedJobDestroyAPIView, SavedJobListCreateAPIView

urlpatterns = [
    path("applications/", ApplicationListCreateAPIView.as_view(), name="application-list-create"),
    path("saved-jobs/", SavedJobListCreateAPIView.as_view(), name="saved-job-list-create"),
    path("saved-jobs/<uuid:job_id>/", SavedJobDestroyAPIView.as_view(), name="saved-job-destroy"),
    path("job-alerts/", JobAlertListCreateAPIView.as_view(), name="job-alert-list-create"),
    path("job-alerts/<uuid:id>/", JobAlertRetrieveUpdateAPIView.as_view(), name="job-alert-detail"),
    path("ai/chat/sessions/", ChatSessionListCreateAPIView.as_view(), name="chat-session-list-create"),
    path("ai/chat/sessions/<uuid:id>/", ChatSessionRetrieveAPIView.as_view(), name="chat-session-detail"),
    path("ai/chat/sessions/<uuid:id>/messages/", ChatMessageCreateAPIView.as_view(), name="chat-message-create"),
    path("ai/interviews/sessions/<uuid:pk>/answers/", InterviewAnswerSubmitView.as_view(), name="interview-answer-submit-alias"),
    path("ai/cover-letters/generate/", CoverLetterGenerateAPIView.as_view(), name="cover-letter-generate"),
    path("ai/salary-estimates/", SalaryEstimateCreateAPIView.as_view(), name="salary-estimate-create"),
]
