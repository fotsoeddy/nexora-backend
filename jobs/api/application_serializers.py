from __future__ import annotations

from rest_framework import serializers

from jobs.models import Application, CV, JobOffer


class ApplicationReadSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    job_offer_id = serializers.UUIDField(source="job_offer.uuid", read_only=True)
    title = serializers.CharField(source="job_offer.title", read_only=True)
    company = serializers.CharField(source="job_offer.company.company_name", read_only=True)
    location = serializers.SerializerMethodField()
    applied = serializers.SerializerMethodField()
    ats_score = serializers.FloatField(source="ai_match_score", allow_null=True)

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

    def get_location(self, obj: Application) -> str:
        parts = [part for part in [obj.job_offer.city, obj.job_offer.country] if part]
        return ", ".join(parts)

    def get_applied(self, obj: Application) -> str:
        return obj.applied_at.isoformat()


class ApplicationCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField()
    cv_id = serializers.UUIDField(required=False)
    cover_letter = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        job_offer = JobOffer.objects.filter(uuid=attrs["job_offer_id"], is_active=True).first()
        if not job_offer:
            raise serializers.ValidationError({"job_offer_id": ["Unknown job offer."]})
        attrs["job_offer"] = job_offer

        cv_id = attrs.get("cv_id")
        if cv_id:
            candidate_profile = self.context["candidate_profile"]
            cv = CV.objects.filter(uuid=cv_id, candidate=candidate_profile, is_active=True).first()
            if not cv:
                raise serializers.ValidationError({"cv_id": ["Unknown CV."]})
            attrs["cv"] = cv

        candidate_profile = self.context["candidate_profile"]
        if Application.objects.filter(
            candidate=candidate_profile,
            job_offer=job_offer,
            is_active=True,
        ).exists():
            raise serializers.ValidationError({"job_offer_id": ["You already applied to this job."]})

        return attrs

    def create(self, validated_data):
        candidate_profile = self.context["candidate_profile"]
        application = Application.objects.create(
            candidate=candidate_profile,
            job_offer=validated_data["job_offer"],
            cv=validated_data.get("cv"),
            cover_letter=validated_data.get("cover_letter", ""),
            ai_match_score=75,
        )
        return application
