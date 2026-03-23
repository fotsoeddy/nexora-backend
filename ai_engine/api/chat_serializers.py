from __future__ import annotations

from rest_framework import serializers

from ai_engine.models import AIChatMessage, AIChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    suggestions = serializers.SerializerMethodField()

    class Meta:
        model = AIChatMessage
        fields = ("id", "role", "content", "suggestions", "created_at")

    def get_suggestions(self, obj: AIChatMessage):
        return obj.metadata.get("suggestions", [])


class ChatSessionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIChatSession
        fields = ("id", "title", "context_type", "messages_count", "messages", "created_at", "updated_at")


class ChatSessionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, max_length=200)
    context_type = serializers.CharField(required=False, allow_blank=True, max_length=30)


class ChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField()
