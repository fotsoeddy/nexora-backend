from __future__ import annotations

import uuid as _uuid

from django.utils.text import slugify
from rest_framework import serializers

from jobs.models import JobDomain, JobOffer, Skill


class JobOfferReadSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    company_name = serializers.CharField(source="company.company_name", read_only=True)
    location = serializers.SerializerMethodField()
    employment_type = serializers.CharField(source="contract_type", read_only=True)
    domain_id = serializers.UUIDField(source="domain.uuid", read_only=True, allow_null=True)
    required_skill_ids = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = (
            "id",
            "title",
            "company_name",
            "location",
            "employment_type",
            "description",
            "requirements",
            "responsibilities",
            "salary_min",
            "salary_max",
            "is_remote",
            "status",
            "domain_id",
            "required_skill_ids",
            "created_at",
            "updated_at",
        )

    def get_location(self, obj: JobOffer) -> str:
        if obj.is_remote and not obj.city:
            return "Remote"
        parts = [part for part in [obj.city, obj.country] if part]
        if not parts and obj.is_remote:
            return "Remote"
        return ", ".join(parts)

    def get_required_skill_ids(self, obj: JobOffer) -> list[str]:
        return [str(skill.uuid) for skill in obj.required_skills.all()]


class JobOfferWriteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    domain_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    required_skill_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = JobOffer
        fields = (
            "id",
            "title",
            "description",
            "requirements",
            "responsibilities",
            "contract_type",
            "experience_level",
            "education_level",
            "salary_min",
            "salary_max",
            "is_salary_visible",
            "city",
            "country",
            "is_remote",
            "application_deadline",
            "status",
            "external_apply_url",
            "is_featured",
            "domain_id",
            "required_skill_ids",
        )
        extra_kwargs = {
            "description": {"required": True},
            "city": {"required": True},
            "country": {"required": False},
            "requirements": {"required": False, "allow_blank": True},
            "responsibilities": {"required": False, "allow_blank": True},
            "education_level": {"required": False, "allow_blank": True},
            "external_apply_url": {"required": False, "allow_blank": True},
        }

    def validate_domain_id(self, value):
        if value is None:
            return None
        domain = JobDomain.objects.filter(uuid=value, is_active=True).first()
        if not domain:
            raise serializers.ValidationError("Unknown job domain.")
        return domain

    def validate_required_skill_ids(self, value):
        skills = list(Skill.objects.filter(uuid__in=value, is_active=True))
        if len(skills) != len(set(value)):
            raise serializers.ValidationError("One or more required skills are invalid.")
        return skills

    def _build_slug(self, title: str) -> str:
        base_slug = slugify(title) or "job-offer"
        return f"{base_slug}-{str(_uuid.uuid4())[:8]}"

    def create(self, validated_data):
        domain = validated_data.pop("domain_id", None)
        required_skills = validated_data.pop("required_skill_ids", [])
        company = self.context["company_profile"]
        validated_data.setdefault("country", "Cameroun")

        job_offer = JobOffer.objects.create(
            company=company,
            domain=domain,
            slug=self._build_slug(validated_data["title"]),
            **validated_data,
        )
        if required_skills:
            job_offer.required_skills.set(required_skills)
        return job_offer

    def update(self, instance, validated_data):
        domain = validated_data.pop("domain_id", serializers.empty)
        required_skills = validated_data.pop("required_skill_ids", serializers.empty)

        if domain is not serializers.empty:
            instance.domain = domain

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if "title" in validated_data:
            instance.slug = self._build_slug(validated_data["title"])

        instance.save()

        if required_skills is not serializers.empty:
            instance.required_skills.set(required_skills)

        return instance
