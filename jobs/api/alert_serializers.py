from __future__ import annotations

from rest_framework import serializers

from jobs.models import JobAlert, JobDomain


class JobAlertSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    domain_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    matches = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = JobAlert
        fields = (
            "id",
            "name",
            "keywords",
            "cities",
            "contract_types",
            "frequency",
            "min_salary",
            "min_match_score",
            "notify_by_email",
            "notify_by_push",
            "is_active",
            "matches",
            "domain_ids",
            "created_at",
            "updated_at",
        )

    def validate_domain_ids(self, value):
        domains = list(JobDomain.objects.filter(uuid__in=value, is_active=True))
        if len(domains) != len(set(value)):
            raise serializers.ValidationError("One or more domains are invalid.")
        return domains

    def create(self, validated_data):
        domains = validated_data.pop("domain_ids", [])
        candidate_profile = self.context["candidate_profile"]
        alert = JobAlert.objects.create(candidate=candidate_profile, **validated_data)
        if domains:
            alert.domains.set(domains)
        return alert

    def update(self, instance, validated_data):
        domains = validated_data.pop("domain_ids", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if domains is not None:
            instance.domains.set(domains)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["domain_ids"] = [str(domain.uuid) for domain in instance.domains.all()]
        return data
