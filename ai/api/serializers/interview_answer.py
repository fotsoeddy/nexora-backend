from rest_framework import serializers
from ai.models import InterviewAnswer

class InterviewAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewAnswer
        fields = '__all__'
