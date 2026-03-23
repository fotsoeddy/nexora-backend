from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ai.api.serializers.saved_job import SavedJobCreateSerializer, SavedJobReadSerializer
from ai.models import SavedJob


class SavedJobListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("job").order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SavedJobCreateSerializer
        return SavedJobReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_job = serializer.save()
        return Response(SavedJobReadSerializer(saved_job).data, status=status.HTTP_201_CREATED)


class SavedJobDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedJobReadSerializer
    lookup_url_kwarg = "job_id"

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def get_object(self):
        return generics.get_object_or_404(self.get_queryset(), job_id=self.kwargs["job_id"])
