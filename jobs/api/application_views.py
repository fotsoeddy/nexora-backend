from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai_engine.api.views import get_or_create_candidate_profile
from jobs.api.application_serializers import ApplicationCreateSerializer, ApplicationReadSerializer
from jobs.emails import send_application_confirmation_email
from jobs.models import Application


class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return (
            Application.objects.filter(candidate=candidate_profile, is_active=True)
            .select_related("job_offer", "job_offer__company")
            .order_by("-applied_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ApplicationCreateSerializer
        return ApplicationReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["candidate_profile"] = get_or_create_candidate_profile(self.request.user)
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        send_application_confirmation_email(application)
        response_serializer = ApplicationReadSerializer(application)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
