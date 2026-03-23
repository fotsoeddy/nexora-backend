import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from ai.utils.cv import extract_text_from_cv
from ai.utils.openai import scan_cv_openai, match_cv_to_job_openai
from ai.models import Job

logger = logging.getLogger(__name__)

class CVScannerAPIView(APIView):
    """
    Endpoint: /api/ai/chatgpt-ats/
    Purpose: Upload a CV, scan it with OpenAI, and return improvements and errors.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        cv_file = request.FILES.get('cv')
        if not cv_file:
            return Response({"error": "No CV file provided. Please upload a 'cv' field."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cv_text = extract_text_from_cv(cv_file, cv_file.name)
            if not cv_text.strip():
                return Response({"error": "Could not extract text from the CV. Ensure it's not empty or an image."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Scan CV using OpenAI
            result = scan_cv_openai(cv_text)
            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error scanning CV")
            return Response({"error": "An internal error occurred while scanning the CV."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JobMatchATSAPIView(APIView):
    """
    Endpoint: /api/ai/job-ats/
    Purpose: Upload a CV and provide a Job ID to match the CV against the job description.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        cv_file = request.FILES.get('cv')
        job_id = request.data.get('job_id')

        if not cv_file:
            return Response({"error": "No CV file provided. Please upload a 'cv' field."}, status=status.HTTP_400_BAD_REQUEST)
        if not job_id:
            return Response({"error": "No job_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch Job
            job = Job.objects.get(id=job_id)
            
            # Extract CV text
            cv_text = extract_text_from_cv(cv_file, cv_file.name)
            if not cv_text.strip():
                return Response({"error": "Could not extract text from the CV."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Match CV to Job using OpenAI
            job_description = f"{job.title}\n\n{job.description}\n\n{job.requirements or ''}"
            result = match_cv_to_job_openai(cv_text, job.title, job_description)
            
            return Response(result, status=status.HTTP_200_OK)

        except Job.DoesNotExist:
            return Response({"error": f"Job with id {job_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error matching CV to job")
            return Response({"error": "An internal error occurred while matching the CV to the job."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
