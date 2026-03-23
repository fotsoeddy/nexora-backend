from __future__ import annotations

from rest_framework import serializers

from ai_engine.models import AICoverLetter
from jobs.models import JobOffer


class CoverLetterGenerateSerializer(serializers.Serializer):
    job_title = serializers.CharField(required=False, allow_blank=True, max_length=255)
    company_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    tone = serializers.CharField(required=False, default="professional", max_length=30)
    job_offer_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        job_offer_id = attrs.get("job_offer_id")
        if job_offer_id:
            job_offer = JobOffer.objects.filter(uuid=job_offer_id, is_active=True).first()
            if not job_offer:
                raise serializers.ValidationError({"job_offer_id": ["Unknown job offer."]})
            attrs["job_offer"] = job_offer
            attrs.setdefault("job_title", job_offer.title)
            attrs.setdefault("company_name", job_offer.company.company_name)

        if not attrs.get("job_title"):
            raise serializers.ValidationError({"job_title": ["This field is required."]})
        if not attrs.get("company_name"):
            raise serializers.ValidationError({"company_name": ["This field is required."]})
        return attrs


class CoverLetterResponseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    generated_text = serializers.CharField(read_only=True)
    job_title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = AICoverLetter
        fields = ("id", "job_title", "company_name", "tone", "generated_text", "created_at")

    def get_job_title(self, obj: AICoverLetter) -> str:
        return obj.job_offer.title if obj.job_offer_id else obj.model_version

    def get_company_name(self, obj: AICoverLetter) -> str:
        if obj.job_offer_id:
            return obj.job_offer.company.company_name
        return obj.user_instructions
