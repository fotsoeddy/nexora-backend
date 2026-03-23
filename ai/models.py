import uuid
from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel, ActivatorModel
from global_data.enum import (
    EmploymentType, AssistantType, SessionType, 
    InterviewType, InterviewStatus, QuestionType, HireReadiness
)

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


class InterviewDifficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"


class Job(BaseModel):
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True, null=True)
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
    name = models.CharField(max_length=100)
    assistant_type = models.CharField(max_length=30, choices=AssistantType.choices)
    vapi_assistant_id = models.CharField(max_length=255, unique=True)
    # is_active field removed because ActivatorModel handles activation state
    # via the `status` field (e.g., Active / Inactive)

    def __str__(self):
        return f"{self.name} ({self.assistant_type})"


class InterviewSession(BaseModel):
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

    session_type = models.CharField(max_length=20, choices=SessionType.choices)
    interview_type = models.CharField(max_length=20, choices=InterviewType.choices, blank=True, null=True)
    
    # Renamed from 'status' to 'interview_status' to avoid clashing with ActivatorModel's 'status'
    interview_status = models.CharField(max_length=30, choices=InterviewStatus.choices, default=InterviewStatus.PENDING)

    # for general flow if no job selected first
    target_job_title = models.CharField(max_length=255, blank=True, null=True)
    target_job_description = models.TextField(blank=True, null=True)
    seniority = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=InterviewDifficulty.choices, default=InterviewDifficulty.MEDIUM)
    question_count = models.PositiveIntegerField(default=5)
    raw_answer_evaluations = models.JSONField(default=dict, blank=True)

    candidate_name = models.CharField(max_length=255, blank=True, null=True)

    # external call provider info
    vapi_call_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.session_type} - {self.interview_status}"


class InterviewQuestion(BaseModel):
    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.MIXED)
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
    session = models.OneToOneField(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    overall_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    hire_readiness = models.CharField(max_length=30, choices=HireReadiness.choices, blank=True, null=True)
    strengths = models.JSONField(default=list, blank=True)
    improvements = models.JSONField(default=list, blank=True)
    summary_to_read_aloud = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Feedback for session {self.session_id}"


class FrontendRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    REVIEWED = "reviewed", "Reviewed"
    SHORTLISTED = "shortlisted", "Shortlisted"
    INTERVIEW = "interview", "Interview"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"


class JobAlertFrequency(models.TextChoices):
    INSTANT = "instant", "Instant"
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"


class AssistantMessageRole(models.TextChoices):
    AI = "ai", "AI"
    USER = "user", "User"


class Application(FrontendRecord):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    cover_letter = models.TextField(blank=True, default="")
    recruiter_notes = models.TextField(blank=True, default="")
    ats_score = models.FloatField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "job"], name="unique_user_job_application"),
        ]

    def __str__(self):
        return f"{self.user} -> {self.job}"


class SavedJob(FrontendRecord):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by_users",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "job"], name="unique_user_saved_job"),
        ]

    def __str__(self):
        return f"Saved {self.job} for {self.user}"


class JobAlert(FrontendRecord):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_alerts",
    )
    name = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    cities = models.JSONField(default=list, blank=True)
    contract_types = models.JSONField(default=list, blank=True)
    frequency = models.CharField(max_length=20, choices=JobAlertFrequency.choices, default=JobAlertFrequency.INSTANT)
    min_salary = models.PositiveIntegerField(blank=True, null=True)
    min_match_score = models.FloatField(blank=True, null=True)
    notify_by_email = models.BooleanField(default=True)
    notify_by_push = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user})"


class AssistantChatSession(FrontendRecord):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assistant_chat_sessions",
    )
    title = models.CharField(max_length=200, default="Career assistant")
    context_type = models.CharField(max_length=60, default="career_advice")

    class Meta:
        ordering = ["-updated_at"]

    @property
    def messages_count(self) -> int:
        return self.messages.count()

    def __str__(self):
        return f"{self.title} ({self.user})"


class AssistantChatMessage(FrontendRecord):
    session = models.ForeignKey(
        AssistantChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=AssistantMessageRole.choices)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role} message in {self.session_id}"


class CoverLetterDraft(FrontendRecord):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cover_letter_drafts",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cover_letter_drafts",
    )
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    tone = models.CharField(max_length=50, default="professional")
    generated_text = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cover letter for {self.job_title}"


class SalaryEstimate(FrontendRecord):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salary_estimates",
    )
    job_title = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    experience_level = models.CharField(max_length=50)
    estimated_min = models.PositiveIntegerField()
    estimated_median = models.PositiveIntegerField()
    estimated_max = models.PositiveIntegerField()
    confidence_level = models.FloatField(default=0.0)
    data_points_used = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Salary estimate for {self.job_title}"
