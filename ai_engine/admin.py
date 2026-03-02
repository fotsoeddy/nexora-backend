from django.contrib import admin

from .models import (
    AIChatMessage,
    AIChatSession,
    AICoverLetter,
    AICVAnalysis,
    AIFormationRecommendation,
    AIInterviewMessage,
    AIInterviewSession,
    AIMatchScore,
    AISalaryEstimate,
    AISearchQuery,
    AIUsageLog,
)


# ─── Inlines ──────────────────────────────────

class AIInterviewMessageInline(admin.TabularInline):
    model = AIInterviewMessage
    extra = 0
    readonly_fields = ("role", "content", "answer_score")


class AIChatMessageInline(admin.TabularInline):
    model = AIChatMessage
    extra = 0
    readonly_fields = ("role", "content")


# ─── Smart Matching ───────────────────────────

@admin.register(AIMatchScore)
class AIMatchScoreAdmin(admin.ModelAdmin):
    list_display = (
        "candidate", "job_offer", "overall_score",
        "skills_score", "experience_score", "created_at",
    )
    list_filter = ("model_version",)
    search_fields = ("candidate__user__email", "job_offer__title")
    raw_id_fields = ("candidate", "job_offer")


# ─── CV Analysis ──────────────────────────────

@admin.register(AICVAnalysis)
class AICVAnalysisAdmin(admin.ModelAdmin):
    list_display = ("cv", "status", "quality_score", "content_score", "keywords_score", "created_at")
    list_filter = ("status", "model_version")
    search_fields = ("cv__candidate__user__email",)
    raw_id_fields = ("cv",)


# ─── Interview ────────────────────────────────

@admin.register(AIInterviewSession)
class AIInterviewSessionAdmin(admin.ModelAdmin):
    list_display = (
        "candidate", "job_offer", "difficulty",
        "overall_score", "status", "questions_count", "created_at",
    )
    list_filter = ("status", "difficulty")
    search_fields = ("candidate__user__email",)
    raw_id_fields = ("candidate", "job_offer")
    inlines = [AIInterviewMessageInline]


# ─── Cover Letter ─────────────────────────────

@admin.register(AICoverLetter)
class AICoverLetterAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job_offer", "tone", "language", "status", "created_at")
    list_filter = ("status", "tone", "language")
    search_fields = ("candidate__user__email",)
    raw_id_fields = ("candidate", "job_offer", "cv")


# ─── Salary Estimation ───────────────────────

@admin.register(AISalaryEstimate)
class AISalaryEstimateAdmin(admin.ModelAdmin):
    list_display = (
        "job_title", "city", "estimated_min",
        "estimated_median", "estimated_max", "confidence_level",
    )
    search_fields = ("job_title", "city")


# ─── NL Search ────────────────────────────────

@admin.register(AISearchQuery)
class AISearchQueryAdmin(admin.ModelAdmin):
    list_display = ("user", "raw_query", "results_count", "was_helpful", "created_at")
    list_filter = ("was_helpful",)
    search_fields = ("user__email", "raw_query")
    raw_id_fields = ("user",)


# ─── Chatbot ──────────────────────────────────

@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "context_type", "messages_count", "is_active", "updated_at")
    list_filter = ("context_type", "is_active")
    search_fields = ("user__email", "title")
    raw_id_fields = ("user",)
    inlines = [AIChatMessageInline]


# ─── Formation Recommendations ───────────────

@admin.register(AIFormationRecommendation)
class AIFormationRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "candidate", "skill_name", "formation_title",
        "provider", "priority", "is_dismissed",
    )
    list_filter = ("recommendation_type", "provider", "is_dismissed")
    search_fields = ("candidate__user__email", "skill_name", "formation_title")
    raw_id_fields = ("candidate",)


# ─── Usage Logs ───────────────────────────────

@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ("user", "feature", "status", "tokens_input", "tokens_output", "cost_estimate", "created_at")
    list_filter = ("feature", "status", "model_name")
    search_fields = ("user__email",)
    raw_id_fields = ("user",)
    date_hierarchy = "created_at"
