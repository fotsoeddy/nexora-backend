from rest_framework import serializers

from ai.models import AssistantChatMessage, AssistantChatSession, CoverLetterDraft, SalaryEstimate


class AssistantChatMessageSerializer(serializers.ModelSerializer):
    suggestions = serializers.SerializerMethodField()

    class Meta:
        model = AssistantChatMessage
        fields = ("id", "role", "content", "suggestions", "created_at")

    def get_suggestions(self, obj):
        return obj.metadata.get("suggestions", [])


class AssistantChatSessionSerializer(serializers.ModelSerializer):
    messages_count = serializers.SerializerMethodField()
    messages = AssistantChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AssistantChatSession
        fields = ("id", "title", "context_type", "messages_count", "messages", "created_at", "updated_at")

    def get_messages_count(self, obj):
        return obj.messages.count()


class AssistantChatSessionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, max_length=200)
    context_type = serializers.CharField(required=False, allow_blank=True, max_length=60)


class AssistantChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField()


class CoverLetterGenerateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField(required=False)
    job_title = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    tone = serializers.CharField(required=False, allow_blank=True, default="professional")

    def validate(self, attrs):
        if not attrs.get("job_offer_id") and not attrs.get("job_title"):
            raise serializers.ValidationError({"job_title": ["Provide a job title or job offer id."]})
        return attrs


class CoverLetterDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetterDraft
        fields = ("id", "job_title", "company_name", "tone", "generated_text", "created_at")


class SalaryEstimateRequestSerializer(serializers.Serializer):
    job_title = serializers.CharField()
    city = serializers.CharField()
    experience_level = serializers.CharField()


class SalaryEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryEstimate
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
