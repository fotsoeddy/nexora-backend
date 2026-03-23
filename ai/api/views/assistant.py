from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai.api.serializers.assistant import (
    AssistantChatMessageCreateSerializer,
    AssistantChatMessageSerializer,
    AssistantChatSessionCreateSerializer,
    AssistantChatSessionSerializer,
    CoverLetterDraftSerializer,
    CoverLetterGenerateSerializer,
    SalaryEstimateRequestSerializer,
    SalaryEstimateSerializer,
)
from ai.models import AssistantChatSession
from ai.services.assistant_workflow import (
    bootstrap_chat_session,
    create_cover_letter,
    create_salary_estimate,
    respond_to_chat_message,
)


class ChatSessionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AssistantChatSession.objects.filter(user=self.request.user).prefetch_related("messages")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AssistantChatSessionCreateSerializer
        return AssistantChatSessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = bootstrap_chat_session(
            user=request.user,
            title=serializer.validated_data.get("title") or "Career assistant",
            context_type=serializer.validated_data.get("context_type") or "career_advice",
        )
        return Response(AssistantChatSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class ChatSessionRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssistantChatSessionSerializer
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return AssistantChatSession.objects.filter(user=self.request.user).prefetch_related("messages")


class ChatMessageCreateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssistantChatMessageCreateSerializer

    def get_queryset(self):
        return AssistantChatSession.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        session = generics.get_object_or_404(self.get_queryset(), pk=kwargs["id"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = respond_to_chat_message(session=session, content=serializer.validated_data["content"])
        return Response(AssistantChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)


class CoverLetterGenerateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CoverLetterGenerateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        draft = create_cover_letter(
            user=request.user,
            job_offer_id=serializer.validated_data.get("job_offer_id"),
            job_title=serializer.validated_data.get("job_title"),
            company_name=serializer.validated_data.get("company_name"),
            tone=serializer.validated_data.get("tone") or "professional",
        )
        return Response(CoverLetterDraftSerializer(draft).data, status=status.HTTP_201_CREATED)


class SalaryEstimateCreateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SalaryEstimateRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estimate = create_salary_estimate(
            user=request.user,
            job_title=serializer.validated_data["job_title"],
            city=serializer.validated_data["city"],
            experience_level=serializer.validated_data["experience_level"],
        )
        return Response(SalaryEstimateSerializer(estimate).data, status=status.HTTP_201_CREATED)
