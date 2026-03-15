import uuid
from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel, ActivatorModel

class BaseModel(TimeStampedModel, ActivatorModel):
    """
    Base model that provides:
    - id: UUID primary key
    - created_at, modified_at (from TimeStampedModel)
    - status, activate_date, deactivate_date (from ActivatorModel)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Job(BaseModel):
    EMPLOYMENT_TYPES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs_created"
    )

    def __str__(self):
        return self.title


class AIAssistant(BaseModel):
    ASSISTANT_TYPES = [
        ("job_interviewer", "Job Interviewer"),
        ("setup_interviewer", "Setup Interviewer"),
    ]

    name = models.CharField(max_length=100)
    assistant_type = models.CharField(max_length=30, choices=ASSISTANT_TYPES)
    vapi_assistant_id = models.CharField(max_length=255, unique=True)
    # is_active field removed because ActivatorModel handles activation state
    # via the `status` field (e.g., Active / Inactive)

    def __str__(self):
        return f"{self.name} ({self.assistant_type})"


class InterviewSession(BaseModel):
    SESSION_TYPES = [
        ("job_based", "Job Based"),
        ("general_setup", "General Setup"),
    ]

    INTERVIEW_TYPES = [
        ("technical", "Technical"),
        ("behavioral", "Behavioral"),
        ("mixed", "Mixed"),
    ]

    SESSION_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("collecting_preferences", "Collecting Preferences"),
        ("questions_generated", "Questions Generated"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("graded", "Graded"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interview_sessions"
    )
    assistant = models.ForeignKey(
        AIAssistant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_sessions"
    )

    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES, blank=True, null=True)
    
    # Renamed from 'status' to 'interview_status' to avoid clashing with ActivatorModel's 'status'
    interview_status = models.CharField(max_length=30, choices=SESSION_STATUS_CHOICES, default="pending")

    # for general flow if no job selected first
    target_job_title = models.CharField(max_length=255, blank=True, null=True)
    target_job_description = models.TextField(blank=True, null=True)
    seniority = models.CharField(max_length=100, blank=True, null=True)
    question_count = models.PositiveIntegerField(default=5)

    candidate_name = models.CharField(max_length=255, blank=True, null=True)

    # external call provider info
    vapi_call_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.session_type} - {self.interview_status}"


class InterviewQuestion(BaseModel):
    QUESTION_TYPES = [
        ("technical", "Technical"),
        ("behavioral", "Behavioral"),
        ("situational", "Situational"),
        ("mixed", "Mixed"),
    ]

    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default="mixed")
    difficulty = models.CharField(max_length=50, blank=True, null=True)
    rubric = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50, default="ai_generated")

    class Meta:
        ordering = ["order"]
        unique_together = ("session", "order")

    def __str__(self):
        return f"Q{self.order} - {self.session_id}"


class InterviewAnswer(BaseModel):
    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    answer_text = models.TextField(blank=True, null=True)
    transcript = models.TextField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    answered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("session", "question")

    def __str__(self):
        return f"Answer for {self.question_id}"


class InterviewFeedback(BaseModel):
    HIRE_READINESS = [
        ("not_ready", "Not Ready"),
        ("needs_practice", "Needs Practice"),
        ("ready", "Ready"),
        ("strong_ready", "Strong Ready"),
    ]

    session = models.OneToOneField(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    overall_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    hire_readiness = models.CharField(max_length=30, choices=HIRE_READINESS, blank=True, null=True)
    strengths = models.JSONField(default=list, blank=True)
    improvements = models.JSONField(default=list, blank=True)
    summary_to_read_aloud = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Feedback for session {self.session_id}"
