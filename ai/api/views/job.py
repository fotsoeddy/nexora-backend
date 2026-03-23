import logging

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.api.serializers.job import JobReadSerializer, JobWriteSerializer
from ai.models import Job

logger = logging.getLogger(__name__)


class JobListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = JobReadSerializer

    def get(self, request):
        jobs = Job.objects.order_by("-created")
        serializer = JobReadSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save(created_by=request.user if request.user.is_authenticated else None)
        logger.info("Job created successfully with id=%s", job.id)
        return Response(JobReadSerializer(job).data, status=status.HTTP_201_CREATED)


class JobDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = JobReadSerializer

    def get_object(self, pk):
        return get_object_or_404(Job, pk=pk)

    def get(self, request, pk):
        job = self.get_object(pk)
        return Response(JobReadSerializer(job).data)

    def put(self, request, pk):
        job = self.get_object(pk)
        serializer = JobWriteSerializer(job, data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        return Response(JobReadSerializer(job).data)

    def delete(self, request, pk):
        job = self.get_object(pk)
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
