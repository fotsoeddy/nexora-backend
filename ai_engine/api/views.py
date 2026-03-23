from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai_engine.api.serializers import (
    InterviewAnswerSubmitSerializer,
    InterviewSessionCreateSerializer,
    InterviewSessionDetailSerializer,
    InterviewSessionGenerateSerializer,
    InterviewSessionListSerializer,
)
from ai_engine.models import AIInterviewSession
from ai_engine.services.interview_service import InterviewService
from jobs.models import CandidateProfile


def get_or_create_candidate_profile(user):
    candidate_profile = getattr(user, "candidate_profile", None)
    if candidate_profile is not None:
        return candidate_profile
    candidate_profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return candidate_profile


class InterviewSessionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return (
            AIInterviewSession.objects.filter(candidate=candidate_profile, is_active=True)
            .select_related("job_offer")
            .prefetch_related("messages")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InterviewSessionCreateSerializer
        return InterviewSessionListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["candidate_profile"] = get_or_create_candidate_profile(self.request.user)
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        response_serializer = InterviewSessionDetailSerializer(session, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class InterviewSessionRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InterviewSessionDetailSerializer
    lookup_field = "uuid"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return (
            AIInterviewSession.objects.filter(candidate=candidate_profile, is_active=True)
            .select_related("job_offer")
            .prefetch_related("messages")
        )


class InterviewSessionGenerateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InterviewSessionGenerateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["candidate_profile"] = get_or_create_candidate_profile(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        response_serializer = InterviewSessionDetailSerializer(session, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class InterviewAnswerSubmitAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InterviewAnswerSubmitSerializer

    def get_queryset(self):
        candidate_profile = get_or_create_candidate_profile(self.request.user)
        return (
            AIInterviewSession.objects.filter(candidate=candidate_profile, is_active=True)
            .select_related("job_offer")
            .prefetch_related("messages")
        )

    def post(self, request, *args, **kwargs):
        session = get_object_or_404(self.get_queryset(), uuid=kwargs["id"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        InterviewService.submit_answer(
            user=request.user,
            session=session,
            content=serializer.validated_data["content"],
        )
        updated_session = get_object_or_404(self.get_queryset(), uuid=kwargs["id"])
        response_serializer = InterviewSessionDetailSerializer(updated_session)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
