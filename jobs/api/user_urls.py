from django.urls import path

from .alert_views import JobAlertListCreateAPIView, JobAlertRetrieveUpdateAPIView
from .application_views import ApplicationListCreateAPIView
from .saved_job_views import SavedJobDestroyAPIView, SavedJobListCreateAPIView

urlpatterns = [
    path("applications/", ApplicationListCreateAPIView.as_view(), name="applications-list"),
    path("saved-jobs/", SavedJobListCreateAPIView.as_view(), name="saved-jobs-list"),
    path("saved-jobs/<uuid:job_id>/", SavedJobDestroyAPIView.as_view(), name="saved-jobs-destroy"),
    path("job-alerts/", JobAlertListCreateAPIView.as_view(), name="job-alerts-list"),
    path("job-alerts/<uuid:id>/", JobAlertRetrieveUpdateAPIView.as_view(), name="job-alerts-detail"),
]
