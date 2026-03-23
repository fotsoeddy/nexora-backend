from rest_framework import serializers

from ai.models import Job


class JobReadSerializer(serializers.ModelSerializer):
    employment_type = serializers.CharField(read_only=True, allow_blank=True, allow_null=True)
    salary_min = serializers.SerializerMethodField()
    salary_max = serializers.SerializerMethodField()
    responsibilities = serializers.SerializerMethodField()
    is_remote = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Job
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
            "created_at",
            "updated_at",
        )

    def get_salary_min(self, obj):
        return None

    def get_salary_max(self, obj):
        return None

    def get_responsibilities(self, obj):
        return ""

    def get_is_remote(self, obj):
        location = (obj.location or "").lower()
        return "remote" in location

    def get_status(self, obj):
        return "active"


class JobWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "company_name",
            "description",
            "requirements",
            "employment_type",
            "location",
        )
        read_only_fields = ("id",)
