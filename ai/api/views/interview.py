from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ai.models import InterviewSession, InterviewQuestion, InterviewFeedback, AIAssistant
from ai.api.serializers import InterviewSessionSerializer, InterviewQuestionSerializer, InterviewFeedbackSerializer
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
        # Vapi sends tool call payload
        # Expected arguments: jobTitle, jobDescription, interviewType, questionCount, etc.
        data = request.data
        tool_call_list = data.get("message", {}).get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            tool_id = tool_call.get("id")
            args = tool_call.get("function", {}).get("arguments", {})
            
            # Here we would normally call an LLM (ChatGPT) to generate questions.
            # For now, we'll return a structured mock response as per the requirement.
            # In a real scenario, you'd use openai library here.
            
            mock_questions = [
                {
                    "id": "q1",
                    "question": f"Based on your experience with {args.get('jobTitle', 'this role')}, how do you handle complex tasks?",
                    "type": args.get("interviewType", "behavioral"),
                    "rubric": "Look for structure and clarity."
                },
                {
                    "id": "q2",
                    "question": "Tell me about a time you faced a difficult challenge and how you overcame it.",
                    "type": "behavioral",
                    "rubric": "Check for problem-solving skills."
                }
            ]
            
            results.append({
                "toolCallId": tool_id,
                "result": {
                    "questions": mock_questions
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
            tool_id = tool_call.get("id")
            args = tool_call.get("function", {}).get("arguments", {})
            
            # args will contain questions, answers, and job metadata
            # Normally, you'd send this to ChatGPT for grading.
            
            mock_grading = {
                "overallScore": 8.5,
                "hireReadiness": "ready",
                "strengths": ["Clear communication", "Good technical depth"],
                "improvements": ["Could provide more specific examples"],
                "summaryToReadAloud": "You performed very well. Your answers were concise and showed deep understanding."
            }
            
            results.append({
                "toolCallId": tool_id,
                "result": mock_grading
            })
            
        return Response({"results": results})
