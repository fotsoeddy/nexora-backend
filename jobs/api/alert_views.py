from __future__ import annotations

from rest_framework import generics, permissions

from ai_engine.api.views import get_or_create_candidate_profile
from jobs.api.alert_serializers import JobAlertSerializer
from jobs.models import JobAlert, JobOffer


class JobAlertListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobAlertSerializer

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return JobAlert.objects.filter(candidate=candidate_profile).prefetch_related("domains").order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["candidate_profile"] = get_or_create_candidate_profile(self.request.user)
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        candidate_profile = get_or_create_candidate_profile(request.user)
        for item, alert in zip(response.data, self.get_queryset()):
            queryset = JobOffer.objects.filter(is_active=True, status="active")
            if alert.keywords:
                queryset = queryset.filter(title__icontains=alert.keywords)
            if alert.cities:
                queryset = queryset.filter(city__in=alert.cities)
            item["matches"] = queryset.count()
        return response


class JobAlertRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobAlertSerializer
    lookup_field = "uuid"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return JobAlert.objects.filter(candidate=candidate_profile).prefetch_related("domains")
