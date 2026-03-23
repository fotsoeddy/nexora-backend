from __future__ import annotations

from rest_framework import serializers

from jobs.api.serializers import JobOfferReadSerializer
from jobs.models import JobOffer, SavedJob


class SavedJobReadSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    saved_at = serializers.DateTimeField(source="created_at", read_only=True)
    job = JobOfferReadSerializer(source="job_offer", read_only=True)

    class Meta:
        model = SavedJob
        fields = ("id", "saved_at", "job")


class SavedJobCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField()

    def validate(self, attrs):
        job_offer = JobOffer.objects.filter(uuid=attrs["job_offer_id"], is_active=True).first()
        if not job_offer:
            raise serializers.ValidationError({"job_offer_id": ["Unknown job offer."]})
        attrs["job_offer"] = job_offer
        return attrs

    def create(self, validated_data):
        candidate_profile = self.context["candidate_profile"]
        saved_job = SavedJob.objects.filter(
            candidate=candidate_profile,
            job_offer=validated_data["job_offer"],
        ).first()
        if saved_job is not None:
            if not saved_job.is_active:
                saved_job.is_active = True
                saved_job.save(update_fields=["is_active", "updated_at"])
            return saved_job

        saved_job = SavedJob.objects.create(
            candidate=candidate_profile,
            job_offer=validated_data["job_offer"],
        )
        return saved_job
