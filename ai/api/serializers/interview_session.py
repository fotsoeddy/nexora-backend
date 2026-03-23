from rest_framework import serializers

from ai.models import InterviewDifficulty, InterviewQuestion, InterviewSession, Job
from global_data.enum import InterviewStatus


class InterviewMessageSerializer(serializers.Serializer):
    id = serializers.CharField()
    role = serializers.ChoiceField(choices=("ai", "user", "system"))
    content = serializers.CharField()
    question_number = serializers.IntegerField(required=False, allow_null=True)
    answer_score = serializers.FloatField(required=False, allow_null=True)
    answer_feedback = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField()


class InterviewSessionListSerializer(serializers.ModelSerializer):
    job_offer_id = serializers.UUIDField(source="job.id", read_only=True, allow_null=True)
    job_title = serializers.SerializerMethodField()
    questions_count = serializers.IntegerField(source="question_count", read_only=True)
    status = serializers.SerializerMethodField()
    overall_score = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="created", read_only=True)

    class Meta:
        model = InterviewSession
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

    def get_job_title(self, obj):
        if obj.job_id:
            return obj.job.title
        return obj.target_job_title or "Interview session"

    def get_status(self, obj):
        if obj.interview_status in {InterviewStatus.GRADED, InterviewStatus.COMPLETED}:
            return "completed"
        if obj.interview_status == InterviewStatus.IN_PROGRESS:
            return "in_progress"
        return obj.interview_status

    def get_overall_score(self, obj):
        if hasattr(obj, "feedback") and obj.feedback.overall_score is not None:
            return float(obj.feedback.overall_score) * 10
        return None


class InterviewSessionDetailSerializer(InterviewSessionListSerializer):
    messages = serializers.SerializerMethodField()
    ai_feedback = serializers.SerializerMethodField()
    communication_score = serializers.SerializerMethodField()
    technical_score = serializers.SerializerMethodField()
    confidence_score = serializers.SerializerMethodField()
    strengths_noted = serializers.SerializerMethodField()
    areas_to_improve = serializers.SerializerMethodField()

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

    def get_messages(self, obj):
        messages = []
        answers_by_question = {
            answer.question_id: answer
            for answer in obj.answers.select_related("question").all()
        }
        evaluations = obj.raw_answer_evaluations or {}

        for question in obj.questions.order_by("order"):
            messages.append(
                {
                    "id": str(question.id),
                    "role": "ai",
                    "content": question.question_text,
                    "question_number": question.order,
                    "created_at": question.created,
                }
            )
            answer = answers_by_question.get(question.id)
            if answer:
                evaluation = evaluations.get(str(question.id), {})
                messages.append(
                    {
                        "id": str(answer.id),
                        "role": "user",
                        "content": answer.answer_text or answer.transcript or "",
                        "question_number": question.order,
                        "answer_score": float(evaluation.get("score", 0)) * 10 if evaluation.get("score") is not None else None,
                        "answer_feedback": evaluation.get("feedback", ""),
                        "created_at": answer.answered_at or answer.created,
                    }
                )

        serializer = InterviewMessageSerializer(messages, many=True)
        return serializer.data

    def get_ai_feedback(self, obj):
        if hasattr(obj, "feedback"):
            return obj.feedback.summary_to_read_aloud
        return ""

    def get_communication_score(self, obj):
        return self._get_component_score(obj, "communication_score")

    def get_technical_score(self, obj):
        return self._get_component_score(obj, "technical_score")

    def get_confidence_score(self, obj):
        return self._get_component_score(obj, "confidence_score")

    def _get_component_score(self, obj, key):
        if hasattr(obj, "feedback"):
            value = (obj.feedback.raw_response or {}).get(key)
            return float(value) * 10 if value is not None else None
        return None

    def get_strengths_noted(self, obj):
        if hasattr(obj, "feedback"):
            return obj.feedback.strengths
        return []

    def get_areas_to_improve(self, obj):
        if hasattr(obj, "feedback"):
            return obj.feedback.improvements
        return []


class InterviewSessionCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField(required=False)
    job_id = serializers.UUIDField(required=False)
    custom_job_title = serializers.CharField(required=False, allow_blank=False, max_length=255)
    difficulty = serializers.ChoiceField(
        choices=InterviewDifficulty.choices,
        required=False,
        default=InterviewDifficulty.MEDIUM,
    )

    def validate(self, attrs):
        if not attrs.get("job_offer_id") and attrs.get("job_id"):
            attrs["job_offer_id"] = attrs["job_id"]

        if not attrs.get("job_offer_id") and not attrs.get("custom_job_title"):
            raise serializers.ValidationError({"detail": "Provide either job_offer_id or custom_job_title."})
        if attrs.get("job_offer_id"):
            job = Job.objects.filter(pk=attrs["job_offer_id"]).first()
            if not job:
                raise serializers.ValidationError({"job_offer_id": ["Unknown job offer."]})
            attrs["job"] = job
        return attrs

    def create(self, validated_data):
        return InterviewSession.objects.create(
            user=self.context["request"].user,
            job=validated_data.get("job"),
            target_job_title=validated_data.get("custom_job_title"),
            difficulty=validated_data.get("difficulty", InterviewDifficulty.MEDIUM),
            session_type="general_setup" if not validated_data.get("job") else "job_based",
            interview_type="mixed",
            interview_status=InterviewStatus.PENDING,
        )


class InterviewSessionGenerateSerializer(InterviewSessionCreateSerializer):
    questions_count = serializers.IntegerField(required=False, min_value=1, max_value=10, default=5)

    def validate(self, attrs):
        if "question_count" in self.initial_data:
            attrs["questions_count"] = int(self.initial_data["question_count"])
        return super().validate(attrs)


class InterviewAnswerSubmitSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=False)
