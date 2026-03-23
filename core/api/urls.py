from django.urls import path

from core.api.views import (
    AdminApplicationDetailView,
    AdminApplicationListView,
    AdminCompanyDetailView,
    AdminCompanyListView,
    AdminDashboardView,
    AdminInterviewDetailView,
    AdminInterviewListView,
    AdminJobAlertDetailView,
    AdminJobDetailView,
    AdminJobListCreateView,
    AdminOperationsView,
    AdminPublicationDetailView,
    AdminPublicationListView,
    AdminUserDetailView,
    AdminUserListView,
)

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("companies/", AdminCompanyListView.as_view(), name="admin-companies"),
    path("companies/<str:company_key>/", AdminCompanyDetailView.as_view(), name="admin-company-detail"),
    path("jobs/", AdminJobListCreateView.as_view(), name="admin-jobs"),
    path("jobs/<uuid:pk>/", AdminJobDetailView.as_view(), name="admin-job-detail"),
    path("publications/", AdminPublicationListView.as_view(), name="admin-publications"),
    path("publications/<uuid:pk>/", AdminPublicationDetailView.as_view(), name="admin-publication-detail"),
    path("applications/", AdminApplicationListView.as_view(), name="admin-applications"),
    path("applications/<uuid:pk>/", AdminApplicationDetailView.as_view(), name="admin-application-detail"),
    path("interviews/", AdminInterviewListView.as_view(), name="admin-interviews"),
    path("interviews/<uuid:pk>/", AdminInterviewDetailView.as_view(), name="admin-interview-detail"),
    path("operations/", AdminOperationsView.as_view(), name="admin-operations"),
    path("job-alerts/<uuid:pk>/", AdminJobAlertDetailView.as_view(), name="admin-job-alert-detail"),
]
