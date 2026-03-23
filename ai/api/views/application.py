from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai.api.serializers.application import ApplicationCreateSerializer, ApplicationReadSerializer
from ai.emails import send_application_confirmation_email
from ai.models import Application


class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Application.objects.filter(user=self.request.user)
            .select_related("job")
            .order_by("-applied_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ApplicationCreateSerializer
        return ApplicationReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        if request.user.email:
            send_application_confirmation_email(application)
        return Response(ApplicationReadSerializer(application).data, status=status.HTTP_201_CREATED)
