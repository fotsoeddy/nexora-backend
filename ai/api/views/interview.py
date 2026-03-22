from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ai.models import InterviewSession, InterviewQuestion, InterviewFeedback, AIAssistant, Job
from ai.api.serializers import InterviewSessionSerializer, InterviewQuestionSerializer, InterviewFeedbackSerializer
from ai.openai_utils import generate_interview_questions_openai, grade_interview_openai
import json

class InterviewSessionListView(APIView):
    """
    List user sessions or start a new session.
    """
    def get(self, request):
        sessions = InterviewSession.objects.filter(user=request.user) if request.user.is_authenticated else InterviewSession.objects.all()
        serializer = InterviewSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InterviewSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user if request.user.is_authenticated else None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InterviewSessionDetailView(APIView):
    """
    Retrieve interview session details.
    """
    def get(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)
        serializer = InterviewSessionSerializer(session)
        return Response(serializer.data)

class VapiGenerateQuestionsView(APIView):
    """
    Endpoint called by Vapi to generate questions.
    """
    def post(self, request):
        data = request.data
        tool_call_list = data.get("message", {}).get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            # Fix 1: use toolCallId with id as fallback
            tool_call_id = tool_call.get("toolCallId") or tool_call.get("id")

            # Fix 2: arguments may arrive as a JSON string
            raw_args = tool_call.get("function", {}).get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args
            
            # Fix 3: use numQuestions (with questionCount fallback for compatibility)
            question_count = args.get('numQuestions') or args.get('questionCount', 5)

            questions_raw = generate_interview_questions_openai(
                job_title=args.get('jobTitle', 'Role'),
                job_description=args.get('jobDescription', ''),
                interview_type=args.get('interviewType', 'mixed'),
                question_count=question_count,
                seniority=args.get('seniority', 'mid'),
                skills=args.get('skills', [])
            )

            # Fix 4: normalize to a predictable question schema
            questions = [
                {
                    "id": q.get("id", f"q{i + 1}"),
                    "order": i + 1,
                    "question": q.get("question", ""),
                    "type": q.get("type", "mixed"),
                    "rubric": q.get("rubric", ""),
                }
                for i, q in enumerate(questions_raw)
            ]
            
            results.append({
                "toolCallId": tool_call_id,
                "result": {
                    "questions": questions
                }
            })
            
        return Response({"results": results})

class VapiGradeInterviewView(APIView):
    """
    Endpoint called by Vapi to grade the interview.
    """
    def post(self, request):
        data = request.data
        tool_call_list = data.get("message", {}).get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            # Fix 1: use toolCallId with id as fallback
            tool_call_id = tool_call.get("toolCallId") or tool_call.get("id")

            # Fix 2: arguments may arrive as a JSON string
            raw_args = tool_call.get("function", {}).get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args
            
            grading_result = grade_interview_openai(
                job_metadata=args.get('job', {}),
                questions_with_answers=args
            )
            
            results.append({
                "toolCallId": tool_call_id,
                "result": grading_result
            })
            
        return Response({"results": results})

class JobInterviewGenerateView(APIView):
    """
    Generate questions for a specific job before the call starts.
    """
    def post(self, request):
        job_id = request.data.get('job_id')
        job = get_object_or_404(Job, pk=job_id)
        
        # Create an interview session
        session = InterviewSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            job=job,
            session_type="job_based",
            interview_status="questions_generated",
            interview_type=request.data.get('interview_type', 'mixed'),
            question_count=request.data.get('question_count', 5)
        )
        
        # Generate questions using OpenAI
        questions_data = generate_interview_questions_openai(
            job_title=job.title,
            job_description=job.description,
            interview_type=session.interview_type,
            question_count=session.question_count
        )
        
        # Save questions to the database
        created_questions = []
        for i, q in enumerate(questions_data):
            question_obj = InterviewQuestion.objects.create(
                session=session,
                order=i + 1,
                question_text=q.get('question'),
                question_type=q.get('type', 'mixed'),
                rubric=q.get('rubric', '')
            )
            created_questions.append({
                "id": str(question_obj.id),
                "question": question_obj.question_text,
                "type": question_obj.question_type,
                "rubric": question_obj.rubric
            })
            
        return Response({
            "session_id": str(session.id),
            "job_title": job.title,
            "questions": created_questions
        }, status=status.HTTP_201_CREATED)
