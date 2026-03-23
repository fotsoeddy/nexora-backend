from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai_engine.api.chat_serializers import (
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    ChatSessionCreateSerializer,
    ChatSessionSerializer,
)
from ai_engine.models import AIChatSession
from ai_engine.services.chat_service import ChatService


class ChatSessionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user, is_active=True).prefetch_related("messages")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ChatSessionCreateSerializer
        return ChatSessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = ChatService.bootstrap_session(
            user=request.user,
            title=serializer.validated_data.get("title") or "Career assistant",
            context_type=serializer.validated_data.get("context_type", "career_advice"),
        )

        return Response(ChatSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class ChatSessionRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSessionSerializer
    lookup_field = "uuid"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user, is_active=True).prefetch_related("messages")


class ChatMessageCreateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageCreateSerializer

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user, is_active=True)

    def post(self, request, *args, **kwargs):
        session = generics.get_object_or_404(self.get_queryset(), uuid=kwargs["id"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ai_message = ChatService.respond_to_message(
            session=session,
            user=request.user,
            content=serializer.validated_data["content"],
        )

        return Response(ChatMessageSerializer(ai_message).data, status=status.HTTP_201_CREATED)
