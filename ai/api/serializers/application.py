from rest_framework import serializers

from ai.models import Application, Job


class ApplicationReadSerializer(serializers.ModelSerializer):
    job_offer_id = serializers.UUIDField(source="job.id", read_only=True)
    title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.CharField(source="job.company_name", read_only=True)
    location = serializers.CharField(source="job.location", read_only=True)
    applied = serializers.DateTimeField(source="applied_at", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "job_offer_id",
            "title",
            "company",
            "location",
            "applied",
            "status",
            "ats_score",
            "cover_letter",
            "recruiter_notes",
            "created_at",
        )


class ApplicationCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField()
    cv_id = serializers.UUIDField(required=False)
    cover_letter = serializers.CharField(required=False, allow_blank=True)

    def validate_job_offer_id(self, value):
        job = Job.objects.filter(pk=value).first()
        if not job:
            raise serializers.ValidationError("Unknown job offer.")
        return job

    def validate(self, attrs):
        user = self.context["request"].user
        job = attrs["job_offer_id"]
        if Application.objects.filter(user=user, job=job).exists():
            raise serializers.ValidationError({"job_offer_id": ["You already applied to this job."]})
        attrs["job"] = job
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Application.objects.create(
            user=user,
            job=validated_data["job"],
            cover_letter=validated_data.get("cover_letter", ""),
            ats_score=78.0,
        )
