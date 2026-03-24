from django.contrib import admin
from .models import (
    Job, AIAssistant, InterviewSession, InterviewQuestion,
    InterviewAnswer, InterviewFeedback, Application, SavedJob,
    JobAlert, AssistantChatSession, AssistantChatMessage,
    CoverLetterDraft, SalaryEstimate, GlobalSettings
)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "employment_type", "location", "created")
    search_fields = ("title", "company_name", "description")
    list_filter = ("employment_type", "status")

@admin.register(AIAssistant)
class AIAssistantAdmin(admin.ModelAdmin):
    list_display = ("name", "assistant_type", "vapi_assistant_id", "status")
    search_fields = ("name", "vapi_assistant_id")
    list_filter = ("assistant_type", "status")

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "session_type", "interview_type", "interview_status", "created")
    search_fields = ("user__username", "candidate_name", "vapi_call_id")
    list_filter = ("session_type", "interview_type", "interview_status")

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ("session", "order", "question_type", "difficulty")
    list_filter = ("question_type", "difficulty", "source")

@admin.register(InterviewAnswer)
class InterviewAnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "answered_at")

@admin.register(InterviewFeedback)
class InterviewFeedbackAdmin(admin.ModelAdmin):
    list_display = ("session", "overall_score", "hire_readiness")
    list_filter = ("hire_readiness",)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("user__username", "job__title")

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at")

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "frequency", "is_active")
    list_filter = ("frequency", "is_active")

@admin.register(AssistantChatSession)
class AssistantChatSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "context_type", "updated_at")
    list_filter = ("context_type",)

@admin.register(AssistantChatMessage)
class AssistantChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "created_at")
    list_filter = ("role",)

@admin.register(CoverLetterDraft)
class CoverLetterDraftAdmin(admin.ModelAdmin):
    list_display = ("job_title", "company_name", "user", "created_at")

@admin.register(SalaryEstimate)
class SalaryEstimateAdmin(admin.ModelAdmin):
    list_display = ("job_title", "city", "experience_level", "estimated_median")

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ("default_minutes_per_assistant",)

    def has_add_permission(self, request):
        # Only allow one instance
        return not GlobalSettings.objects.exists()
