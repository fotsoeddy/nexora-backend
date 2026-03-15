from rest_framework import serializers
from ai.models import AIAssistant

class AIAssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAssistant
        fields = '__all__'
