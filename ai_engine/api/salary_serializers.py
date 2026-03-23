from __future__ import annotations

from rest_framework import serializers

from ai_engine.models import AISalaryEstimate


class SalaryEstimateRequestSerializer(serializers.Serializer):
    job_title = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=120)
    experience_level = serializers.CharField(max_length=20)


class SalaryEstimateResponseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = AISalaryEstimate
        fields = (
            "id",
            "job_title",
            "city",
            "experience_level",
            "estimated_min",
            "estimated_median",
            "estimated_max",
            "confidence_level",
            "data_points_used",
            "explanation",
            "created_at",
        )
