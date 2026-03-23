from django.urls import path

from .views import JobListCreateAPIView, JobRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", JobListCreateAPIView.as_view(), name="ai-jobs-list"),
    path("<uuid:id>/", JobRetrieveUpdateDestroyAPIView.as_view(), name="ai-jobs-detail"),
]
