from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ai.models import Job
from ai.api.serializers import JobSerializer
import logging

logger = logging.getLogger(__name__)

class JobListView(APIView):
    """
    List all jobs or create a new job.
    """
    def get(self, request):
        logger.info(f"JobListView.get called by user: {request.user}")
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"JobListView.post called with data: {request.data}")
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user if request.user.is_authenticated else None)
            logger.info(f"Job created successfully with id: {serializer.data.get('id')}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Job creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobDetailView(APIView):
    """
    Retrieve, update or delete a job instance.
    """
    def get_object(self, pk):
        return get_object_or_404(Job, pk=pk)

    def get(self, request, pk):
        logger.info(f"JobDetailView.get called for pk: {pk}")
        job = self.get_object(pk)
        serializer = JobSerializer(job)
        return Response(serializer.data)

    def put(self, request, pk):
        logger.info(f"JobDetailView.put called for pk: {pk} with data: {request.data}")
        job = self.get_object(pk)
        serializer = JobSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Job {pk} updated successfully")
            return Response(serializer.data)
        logger.warning(f"Job {pk} update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        logger.info(f"JobDetailView.delete called for pk: {pk}")
        job = self.get_object(pk)
        job.delete()
        logger.info(f"Job {pk} deleted successfully")
        return Response(status=status.HTTP_204_NO_CONTENT)
