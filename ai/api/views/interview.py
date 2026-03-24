from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ai.models import InterviewSession, InterviewQuestion, InterviewFeedback, AIAssistant, Job
from ai.api.serializers import (
    InterviewAnswerSerializer,
    InterviewAnswerSubmitSerializer,
    InterviewFeedbackSerializer,
    InterviewQuestionSerializer,
    InterviewSessionCreateSerializer,
    InterviewSessionDetailSerializer,
    InterviewSessionGenerateSerializer,
    InterviewSessionListSerializer,
)
from ai.utils.openai import generate_interview_questions_openai, grade_interview_openai
from ai.services.interview_workflow import (
    evaluate_answer_inline,
    finalize_interview_feedback,
    get_next_unanswered_question,
    save_interview_answer,
)
from global_data.enum import InterviewStatus
import json
import logging

logger = logging.getLogger(__name__)



class IsVapiWebhook(BasePermission):
    """
    Allows access only to requests carrying the correct Vapi webhook Bearer token.
    """
    def has_permission(self, request, view):
        # Log all headers for deep debugging of Vapi requests
        all_headers = {k: v for k, v in request.headers.items()}
        logger.info(f"IsVapiWebhook: Request Headers: {all_headers}")

        auth = request.headers.get("Authorization", "")
        expected_token = getattr(settings, "VAPI_WEBHOOK_TOKEN", None)
        
        logger.info(f"IsVapiWebhook: Checking permission for {view.__class__.__name__}")
        logger.info(f"IsVapiWebhook: Authorization Header: {auth}")
        logger.info(f"IsVapiWebhook: Expected Token: Bearer {expected_token[:12] if expected_token else 'None'}... [truncated]")

        if not expected_token:
            logger.error("IsVapiWebhook: VAPI_WEBHOOK_TOKEN is not set in settings!")
            return False

        if auth == f"Bearer {expected_token}":
            logger.info("IsVapiWebhook: Permission GRANTED (Token match)")
            return True
        
        # Detailed comparison for debugging
        if expected_token:
            auth_val = auth.replace("Bearer ", "").strip()
            logger.info(f"IsVapiWebhook: Comparing tokens... Expected start: {expected_token[:4]}..., Got start: {auth_val[:4]}...")
            if auth_val == expected_token:
                 logger.info("IsVapiWebhook: Permission GRANTED (Token match after normalization)")
                 return True

        # Fallback for development/debugging if explicitly allowed via DEBUG
        if getattr(settings, "DEBUG", False) and not auth:
            logger.warning("IsVapiWebhook: Permission GRANTED (DEBUG mode bypass for empty Auth header)")
            return True

        logger.warning(f"IsVapiWebhook: Permission DENIED. Auth header present: {bool(auth)}, Expected prefix: 'Bearer {expected_token[:4] if expected_token else 'None'}'")
        return False

class InterviewSessionListView(APIView):
    """
    List user sessions or start a new session.
    """
    serializer_class = InterviewSessionListSerializer

    def get(self, request):
        logger.info(f"InterviewSessionListView.get called by user: {request.user}")
        sessions = (
            InterviewSession.objects.filter(user=request.user).order_by("-created")
            if request.user.is_authenticated
            else InterviewSession.objects.all().order_by("-created")
        )
        serializer = InterviewSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"InterviewSessionListView.post called with data: {request.data}")
        serializer = InterviewSessionCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        logger.info("InterviewSession created successfully")
        return Response(InterviewSessionDetailSerializer(session).data, status=status.HTTP_201_CREATED)

class InterviewSessionDetailView(APIView):
    """
    Retrieve interview session details.
    """
    serializer_class = InterviewSessionDetailSerializer

    def get(self, request, pk):
        logger.info(f"InterviewSessionDetailView.get called for pk: {pk}")
        session = get_object_or_404(InterviewSession, pk=pk)
        serializer = InterviewSessionDetailSerializer(session)
        return Response(serializer.data)


class InterviewAnswerSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewAnswerSubmitSerializer

    def post(self, request, pk):
        logger.info(f"InterviewAnswerSubmitView.post called for session: {pk}")
        session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        question_id = request.data.get("question_id")
        answer_text = request.data.get("answer_text") or request.data.get("content", "")
        transcript = request.data.get("transcript", "") or answer_text

        if not answer_text and not transcript:
            return Response({"detail": "Provide answer_text or transcript."}, status=status.HTTP_400_BAD_REQUEST)

        if question_id:
            question = get_object_or_404(InterviewQuestion, pk=question_id, session=session)
        else:
            question = get_next_unanswered_question(session)
            if not question:
                return Response({"detail": "No remaining interview question."}, status=status.HTTP_400_BAD_REQUEST)

        answer = save_interview_answer(
            session=session,
            question=question,
            answer_text=answer_text,
            transcript=transcript,
            duration_seconds=request.data.get("duration_seconds"),
        )
        evaluation = evaluate_answer_inline(
            session=session,
            question=question,
            answer_text=answer.answer_text or answer.transcript or "",
        )
        session.raw_answer_evaluations[str(question.id)] = evaluation
        session.save(update_fields=["raw_answer_evaluations", "modified"])

        if session.answers.count() >= session.question_count:
            finalize_interview_feedback(session=session)
            session.refresh_from_db()
            session.interview_status = InterviewStatus.COMPLETED
            session.save(update_fields=["interview_status", "modified"])

        serializer = InterviewSessionDetailSerializer(session)
        data = serializer.data
        data["latest_answer"] = InterviewAnswerSerializer(answer).data
        data["latest_answer_evaluation"] = evaluation
        return Response(data, status=status.HTTP_200_OK)

class VapiGenerateQuestionsView(APIView):
    """
    Endpoint called by Vapi to generate questions.
    """
    permission_classes = [IsVapiWebhook]
    def post(self, request):
        logger.info(f"VapiGenerateQuestionsView.post called with data: {request.data}")
        data = request.data
        tool_call_list = data.get("message", {}).get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            tool_call_id = tool_call.get("toolCallId") or tool_call.get("id")
            raw_args = tool_call.get("function", {}).get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args
            
            question_count = args.get('numQuestions') or args.get('questionCount', 5)

            questions_raw = generate_interview_questions_openai(
                job_title=args.get('jobTitle', 'Role'),
                job_description=args.get('jobDescription', ''),
                interview_type=args.get('interviewType', 'mixed'),
                question_count=question_count,
                seniority=args.get('seniority', 'mid'),
                skills=args.get('skills', [])
            )

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
            
        logger.info(f"VapiGenerateQuestionsView returning {len(results)} results")
        return Response({"results": results})

class VapiGradeInterviewView(APIView):
    """
    Endpoint called by Vapi to grade the interview.
    """
    permission_classes = [IsVapiWebhook]
    def post(self, request):
        logger.info(f"VapiGradeInterviewView.post called with data: {request.data}")
        data = request.data
        tool_call_list = data.get("message", {}).get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            tool_call_id = tool_call.get("toolCallId") or tool_call.get("id")
            raw_args = tool_call.get("function", {}).get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args
            session_id = args.get("sessionId")
            session = InterviewSession.objects.filter(pk=session_id).first() if session_id else None
            if session:
                grading_result = finalize_interview_feedback(session=session)
                grading_result = InterviewFeedbackSerializer(grading_result).data
            else:
                grading_result = grade_interview_openai(
                    job_metadata=args.get('job', {}),
                    questions_with_answers=args
                )
            
            results.append({
                "toolCallId": tool_call_id,
                "result": grading_result
            })
            
        logger.info(f"VapiGradeInterviewView returning {len(results)} results")
        return Response({"results": results})


class VapiSaveAnswerView(APIView):
    """
    Endpoint called by Vapi after each question to save the candidate answer.
    """
    authentication_classes = []
    permission_classes = [IsVapiWebhook]
    
    def post(self, request):
        logger.info(f"VapiSaveAnswerView.post called with data: {request.data}")
        data = request.data
        tool_call_list = data.get("message", {}).get("toolCallList", [])
        results = []

        for tool_call in tool_call_list:
            tool_call_id = tool_call.get("toolCallId") or tool_call.get("id")
            raw_args = tool_call.get("function", {}).get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args

            session = get_object_or_404(InterviewSession, pk=args.get("sessionId"))
            question = get_object_or_404(InterviewQuestion, pk=args.get("questionId"), session=session)
            answer = save_interview_answer(
                session=session,
                question=question,
                answer_text=args.get("answer", ""),
                transcript=args.get("transcript", args.get("answer", "")),
                duration_seconds=args.get("durationSeconds"),
            )

            results.append({
                "toolCallId": tool_call_id,
                "result": {"ok": True, "answerId": str(answer.id)}
            })

        logger.info(f"VapiSaveAnswerView returning {len(results)} results")
        return Response({"results": results})

class VapiToolsView(APIView):
    """
    Central dispatcher for all Vapi tool calls.
    """
    authentication_classes = []
    permission_classes = [IsVapiWebhook]

    def post(self, request):
        data = request.data
        message = data.get("message", {})
        message_type = message.get("type", "tool-calls")
        call_id = data.get("call", {}).get("id") or message.get("call", {}).get("id") or data.get("callId")

        logger.info(f"VapiToolsView: Incoming POST request ({message_type}) for call {call_id}")
        
        # 1. Handle End of Call Report to accurately record duration
        if message_type == "end-of-call-report":
            duration = data.get("durationSeconds") or message.get("durationSeconds") or data.get("duration") or 0
            logger.info(f"VapiToolsView: Received end-of-call report. Call: {call_id}, Duration: {duration}s")
            
            if call_id:
                session = InterviewSession.objects.filter(vapi_call_id=call_id).first()
                if session:
                    # Back-calculate started_at if it's missing (shouldn't happen but safe)
                    if not session.started_at:
                        session.started_at = timezone.now() - timedelta(seconds=float(duration))
                    
                    session.completed_at = session.started_at + timedelta(seconds=float(duration))
                    session.interview_status = InterviewStatus.COMPLETED
                    session.save(update_fields=["completed_at", "started_at", "interview_status", "modified"])
                    logger.info(f"VapiToolsView: Recorded final duration {duration}s for session {session.id}")
            
            return Response({"ok": True})

        # 2. Handle Tool Calls
        tool_calls = message.get("toolCallList", [])
        results = []

        for tc in tool_calls:
            tool_call_id = tc.get("toolCallId") or tc.get("id")
            fn = tc.get("function", {}) or {}
            name = fn.get("name")

            raw_args = fn.get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args

            logger.info(f"VapiToolsView: Processing tool {name} (id: {tool_call_id})")
            
            # Auto-link the session and START the timer if not already started
            session_id = args.get("sessionId")
            if session_id and call_id:
                session_filter = InterviewSession.objects.filter(pk=session_id)
                # Update call ID if missing
                session_filter.filter(vapi_call_id__isnull=True).update(vapi_call_id=call_id)
                # START the timer if missing - this is crucial for time tracking!
                session_filter.filter(started_at__isnull=True).update(started_at=timezone.now())
                logger.info(f"VapiToolsView: Ensured session {session_id} has started_at and call_id")

            if name == "generate_interview_questions":
                job_id = args.get("jobId")
                interview_type = args.get("interviewType", "mixed")
                num_questions = args.get("numQuestions") or args.get("questionCount", 5)

                # Skip job lookup if jobId is N/A or missing
                if job_id and str(job_id).lower() not in ["na", "none", "null", "n/a"]:
                    logger.info(f"VapiToolsView: Fetching job details for jobId: {job_id}")
                    job = get_object_or_404(Job, pk=job_id)
                    job_title = job.title
                    job_description = (job.description or "") + "\n\nRequirements:\n" + (job.requirements or "")
                else:
                    logger.info("VapiToolsView: No valid jobId provided, using jobTitle/jobDescription from args")
                    job_title = args.get("jobTitle", "Role")
                    job_description = args.get("jobDescription", "")

                questions_raw = generate_interview_questions_openai(
                    job_title=job_title,
                    job_description=job_description,
                    interview_type=interview_type,
                    question_count=num_questions,
                    seniority=args.get("seniority", "mid"),
                    skills=args.get("skills", []),
                )
                questions = [
                    {
                        "id": q.get("id", f"q{i+1}"),
                        "order": i + 1,
                        "question": q.get("question", ""),
                        "type": q.get("type", interview_type),
                        "rubric": q.get("rubric", ""),
                    }
                    for i, q in enumerate(questions_raw)
                ]
                result = {"questions": questions}

            elif name == "create_interview_session":
                interview_type = args.get("interviewType", "mixed")
                num_questions = args.get("numQuestions") or args.get("questionCount", 5)

                job_id = args.get("jobId")
                if job_id and str(job_id).lower() not in ["na", "none", "null", "n/a"]:
                    job = Job.objects.filter(pk=job_id).first()
                else:
                    job = None

                logger.info(f"VapiToolsView: Creating voice-first session. Job: {job.title if job else 'None'}")

                user_id = args.get("userId")
                user = User.objects.filter(id=user_id).first() if user_id else None

                session = InterviewSession.objects.create(
                    user=user,
                    job=job,
                    target_job_title=args.get("jobTitle", ""),
                    session_type="voice_first",
                    interview_status="created",
                    interview_type=interview_type,
                    question_count=num_questions,
                    candidate_name=args.get("candidateName", ""),
                    vapi_call_id=call_id,
                    started_at=timezone.now() # START the timer immediately
                )

                result = {
                    "sessionId": str(session.id),
                    "jobTitle": (job.title if job else args.get("jobTitle", "Interview")),
                }

            elif name == "save_interview_answer":
                session_id = args.get("sessionId")
                question_id = args.get("questionId")
                logger.info(f"VapiToolsView: Saving answer for session {session_id}, question {question_id}")
                
                session = get_object_or_404(InterviewSession, pk=session_id)
                question = get_object_or_404(InterviewQuestion, pk=question_id, session=session)
                answer = save_interview_answer(
                    session=session,
                    question=question,
                    answer_text=args.get("answer", ""),
                    transcript=args.get("transcript", args.get("answer", "")),
                    duration_seconds=args.get("durationSeconds"),
                )
                result = {"ok": True, "answerId": str(answer.id)}

            elif name == "grade_interview":
                logger.info(f"VapiToolsView: Grading interview for session {args.get('sessionId')}")
                result = grade_interview_openai(
                    job_metadata=args.get("job", {}),
                    questions_with_answers=args,
                )

            else:
                logger.warning(f"VapiToolsView: Unknown tool called: {name}")
                result = {"error": f"Unknown tool: {name}"}

            results.append({"toolCallId": tool_call_id, "result": result})

        logger.info(f"VapiToolsView: Returning {len(results)} results")
        return Response({"results": results})

class JobInterviewGenerateView(APIView):
    """
    Generate questions for a specific job before the call starts.
    """
    serializer_class = InterviewSessionGenerateSerializer

    def post(self, request):
        logger.info(f"JobInterviewGenerateView.post called with data: {request.data}")
        serializer = InterviewSessionGenerateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        job = serializer.validated_data.get("job")
        custom_job_title = serializer.validated_data.get("custom_job_title", "")
        difficulty = serializer.validated_data.get("difficulty", "medium")
        question_count = serializer.validated_data.get("questions_count", 5)

        # Optimization: Try to reuse existing questions for this job
        questions_data = []
        if job:
            # Look for questions from previous sessions of the same job to avoid redundant OpenAI calls
            # We pick the most recent session's questions that match the requested count
            prev_session = InterviewSession.objects.filter(job=job).order_by('-created').first()
            if prev_session:
                existing_qs = InterviewQuestion.objects.filter(session=prev_session).order_by('order')[:question_count]
                if existing_qs.count() >= question_count:
                    logger.info(f"JobInterviewGenerateView: Reusing {question_count} questions from previous session {prev_session.id}")
                    for eq in existing_qs:
                        questions_data.append({
                            'question': eq.question_text,
                            'type': eq.question_type,
                            'rubric': eq.rubric
                        })

        # Create an interview session
        session = InterviewSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            job=job,
            target_job_title=custom_job_title,
            session_type="job_based" if job else "general_setup",
            interview_status="questions_generated",
            interview_type=request.data.get('interview_type', 'mixed'),
            difficulty=difficulty,
            question_count=question_count,
        )

        # Generate new questions if none were reused
        if not questions_data:
            logger.info("JobInterviewGenerateView: Generating new questions via OpenAI")
            questions_data = generate_interview_questions_openai(
                job_title=job.title if job else custom_job_title,
                job_description=job.description if job else request.data.get("job_description", ""),
                interview_type=session.interview_type,
                question_count=session.question_count
            )
        
        # Save questions to the database for this specific session
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
            
        logger.info(f"JobInterviewGenerateView: Session {session.id} ready with {len(created_questions)} questions")
        return Response(InterviewSessionDetailSerializer(session).data, status=status.HTTP_201_CREATED)
