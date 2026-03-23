from rest_framework import serializers

from ai.api.serializers.job import JobReadSerializer
from ai.models import Job, SavedJob


class SavedJobReadSerializer(serializers.ModelSerializer):
    saved_at = serializers.DateTimeField(source="created_at", read_only=True)
    job = JobReadSerializer(read_only=True)

    class Meta:
        model = SavedJob
        fields = ("id", "saved_at", "job")


class SavedJobCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField()

    def validate_job_offer_id(self, value):
        job = Job.objects.filter(pk=value).first()
        if not job:
            raise serializers.ValidationError("Unknown job offer.")
        return job

    def create(self, validated_data):
        user = self.context["request"].user
        saved_job, _ = SavedJob.objects.get_or_create(
            user=user,
            job=validated_data["job_offer_id"],
        )
        return saved_job
