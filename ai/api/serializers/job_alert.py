from rest_framework import serializers

from ai.models import JobAlert


class JobAlertSerializer(serializers.ModelSerializer):
    matches = serializers.IntegerField(read_only=True, default=0)
    domain_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        default=list,
    )

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
        read_only_fields = ("id", "created_at", "updated_at", "matches")

    def create(self, validated_data):
        validated_data.pop("domain_ids", None)
        return JobAlert.objects.create(user=self.context["request"].user, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("domain_ids", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
