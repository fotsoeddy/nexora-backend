from rest_framework import serializers
from ai.models import InterviewSession
from ai.api.serializers.interview_answer import InterviewAnswerSerializer
from ai.api.serializers.interview_feedback import InterviewFeedbackSerializer
from ai.api.serializers.interview_question import InterviewQuestionSerializer

class InterviewSessionSerializer(serializers.ModelSerializer):
    questions = InterviewQuestionSerializer(many=True, read_only=True)
    answers = InterviewAnswerSerializer(many=True, read_only=True)
    feedback = InterviewFeedbackSerializer(read_only=True)

    class Meta:
        model = InterviewSession
        fields = '__all__'
        read_only_fields = ("user", "assistant", "vapi_call_id", "started_at", "completed_at")
