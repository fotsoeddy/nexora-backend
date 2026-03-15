from rest_framework import serializers
from ai.models import InterviewFeedback

class InterviewFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewFeedback
        fields = '__all__'
