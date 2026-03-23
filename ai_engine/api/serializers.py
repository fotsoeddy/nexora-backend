from __future__ import annotations

from rest_framework import serializers

from ai_engine.models import AIInterviewMessage, AIInterviewSession, InterviewDifficulty
from jobs.models import JobOffer


class InterviewMessageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = AIInterviewMessage
        fields = (
            "id",
            "role",
            "content",
            "question_number",
            "answer_score",
            "answer_feedback",
            "created_at",
        )


class InterviewSessionListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    job_offer_id = serializers.UUIDField(source="job_offer.uuid", read_only=True, allow_null=True)
    job_title = serializers.SerializerMethodField()

    class Meta:
        model = AIInterviewSession
        fields = (
            "id",
            "job_offer_id",
            "job_title",
            "difficulty",
            "status",
            "questions_count",
            "overall_score",
            "started_at",
            "completed_at",
            "created_at",
        )

    def get_job_title(self, obj: AIInterviewSession) -> str:
        if obj.job_offer_id:
            return obj.job_offer.title
        return obj.custom_job_title


class InterviewSessionDetailSerializer(InterviewSessionListSerializer):
    messages = InterviewMessageSerializer(many=True, read_only=True)

    class Meta(InterviewSessionListSerializer.Meta):
        fields = InterviewSessionListSerializer.Meta.fields + (
            "messages",
            "ai_feedback",
            "communication_score",
            "technical_score",
            "confidence_score",
            "strengths_noted",
            "areas_to_improve",
        )


class InterviewSessionCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField(required=False)
    custom_job_title = serializers.CharField(required=False, allow_blank=False, max_length=200)
    difficulty = serializers.ChoiceField(
        choices=InterviewDifficulty.choices,
        required=False,
        default=InterviewDifficulty.MEDIUM,
    )

    def validate(self, attrs):
        job_offer_id = attrs.get("job_offer_id")
        custom_job_title = attrs.get("custom_job_title")

        if not job_offer_id and not custom_job_title:
            raise serializers.ValidationError(
                {"detail": "Provide either job_offer_id or custom_job_title."}
            )

        if job_offer_id:
            job_offer = JobOffer.objects.filter(uuid=job_offer_id, is_active=True).first()
            if not job_offer:
                raise serializers.ValidationError({"job_offer_id": ["Unknown job offer."]})
            attrs["job_offer"] = job_offer

        return attrs

    def create(self, validated_data):
        candidate_profile = self.context["candidate_profile"]
        job_offer = validated_data.pop("job_offer", None)
        return AIInterviewSession.objects.create(
            candidate=candidate_profile,
            job_offer=job_offer,
            custom_job_title=validated_data.get("custom_job_title", ""),
            difficulty=validated_data["difficulty"],
        )


class InterviewSessionGenerateSerializer(InterviewSessionCreateSerializer):
    questions_count = serializers.IntegerField(required=False, min_value=1, max_value=10, default=5)

    def create(self, validated_data):
        from ai_engine.services.interview_service import InterviewService

        questions_count = validated_data.pop("questions_count", 5)
        candidate_profile = self.context["candidate_profile"]
        job_offer = validated_data.pop("job_offer", None)
        return InterviewService.generate_session(
            user=candidate_profile.user,
            candidate_profile=candidate_profile,
            job_offer=job_offer,
            custom_job_title=validated_data.get("custom_job_title", ""),
            difficulty=validated_data["difficulty"],
            questions_count=questions_count,
        )


class InterviewAnswerSubmitSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=False)
