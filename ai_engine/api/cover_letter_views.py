from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai_engine.api.cover_letter_serializers import (
    CoverLetterGenerateSerializer,
    CoverLetterResponseSerializer,
)
from ai_engine.api.views import get_or_create_candidate_profile
from ai_engine.services.cover_letter_service import CoverLetterService


class CoverLetterGenerateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CoverLetterGenerateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        candidate_profile = get_or_create_candidate_profile(request.user)
        job_offer = serializer.validated_data.get("job_offer")
        job_title = serializer.validated_data["job_title"]
        company_name = serializer.validated_data["company_name"]
        tone = serializer.validated_data["tone"]
        cover_letter = CoverLetterService.generate(
            user=request.user,
            candidate_profile=candidate_profile,
            job_offer=job_offer,
            job_title=job_title,
            company_name=company_name,
            tone=tone,
        )

        response_serializer = CoverLetterResponseSerializer(cover_letter)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
