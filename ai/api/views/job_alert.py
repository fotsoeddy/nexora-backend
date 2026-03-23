from rest_framework import generics, permissions

from ai.api.serializers.job_alert import JobAlertSerializer
from ai.models import Job, JobAlert


class JobAlertListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobAlertSerializer

    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        for item, alert in zip(response.data, self.get_queryset()):
            queryset = Job.objects.all()
            if alert.keywords:
                queryset = queryset.filter(title__icontains=alert.keywords)
            if alert.cities:
                queryset = queryset.filter(location__in=alert.cities)
            if alert.contract_types:
                queryset = queryset.filter(employment_type__in=alert.contract_types)
            item["matches"] = queryset.count()
        return response


class JobAlertRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobAlertSerializer
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
