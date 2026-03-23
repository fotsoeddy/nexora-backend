from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai_engine.api.views import get_or_create_candidate_profile
from jobs.api.saved_job_serializers import SavedJobCreateSerializer, SavedJobReadSerializer
from jobs.models import SavedJob


class SavedJobListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return (
            SavedJob.objects.filter(candidate=candidate_profile, is_active=True)
            .select_related("job_offer", "job_offer__company")
            .prefetch_related("job_offer__required_skills")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SavedJobCreateSerializer
        return SavedJobReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["candidate_profile"] = get_or_create_candidate_profile(self.request.user)
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_job = serializer.save()
        response_serializer = SavedJobReadSerializer(saved_job)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class SavedJobDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "job_offer__uuid"
    lookup_url_kwarg = "job_id"

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return SavedJob.objects.filter(candidate=candidate_profile, is_active=True)

    def perform_destroy(self, instance):
        instance.soft_delete()
