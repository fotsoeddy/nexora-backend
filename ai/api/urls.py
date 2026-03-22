from django.urls import path
from ai.api.views.job import JobListView, JobDetailView
from ai.api.views.interview import (
    InterviewSessionListView, 
    InterviewSessionDetailView, 
    VapiGenerateQuestionsView, 
    VapiGradeInterviewView,
    VapiSaveAnswerView,
    JobInterviewGenerateView
)

urlpatterns = [
    # Job endpoints
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<uuid:pk>/', JobDetailView.as_view(), name='job-detail'),
    
    # Interview session endpoints
    path('interviews/sessions/', InterviewSessionListView.as_view(), name='interview-session-list'),
    path('interviews/sessions/generate/', JobInterviewGenerateView.as_view(), name='job-interview-generate'),
    path('interviews/sessions/<uuid:pk>/', InterviewSessionDetailView.as_view(), name='interview-session-detail'),
    
    # Vapi tool endpoints
    path('vapi/generate-questions/', VapiGenerateQuestionsView.as_view(), name='vapi-generate-questions'),
    path('vapi/grade-interview/', VapiGradeInterviewView.as_view(), name='vapi-grade-interview'),
    path('vapi/save-answer/', VapiSaveAnswerView.as_view(), name='vapi-save-answer'),
]
