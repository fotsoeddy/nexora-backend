from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai_engine.api.salary_serializers import (
    SalaryEstimateRequestSerializer,
    SalaryEstimateResponseSerializer,
)
from ai_engine.services.salary_service import SalaryService


class SalaryEstimateCreateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SalaryEstimateRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estimate = SalaryService.estimate(
            user=request.user,
            job_title=serializer.validated_data["job_title"],
            city=serializer.validated_data["city"],
            experience_level=serializer.validated_data["experience_level"],
        )
        response_serializer = SalaryEstimateResponseSerializer(estimate)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
