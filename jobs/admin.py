from django.contrib import admin

from .models import (
    Application,
    CandidateProfile,
    CompanyProfile,
    CV,
    CVSkill,
    Education,
    Experience,
    JobAlert,
    JobDomain,
    JobOffer,
    PricingPlan,
    Skill,
    Subscription,
)


# ─── Inlines ──────────────────────────────────

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class CVSkillInline(admin.TabularInline):
    model = CVSkill
    extra = 0
    autocomplete_fields = ["skill"]


# ─── Profiles ─────────────────────────────────

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "experience_level", "is_available", "created_at")
    list_filter = ("experience_level", "is_available", "country")
    search_fields = ("user__email", "user__first_name", "user__last_name", "city")
    raw_id_fields = ("user",)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "industry", "city", "is_verified", "created_at")
    list_filter = ("is_verified", "country")
    search_fields = ("company_name", "user__email", "industry")
    raw_id_fields = ("user",)


# ─── Jobs ─────────────────────────────────────

@admin.register(JobDomain)
class JobDomainAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "domain", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("domain", "is_active")


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = (
        "title", "company", "domain", "contract_type",
        "city", "status", "application_deadline", "created_at",
    )
    list_filter = ("status", "contract_type", "domain", "is_featured", "is_remote")
    search_fields = ("title", "company__company_name", "city")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("company",)
    date_hierarchy = "created_at"


# ─── CV ───────────────────────────────────────

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ("title", "candidate", "is_primary", "is_public", "ai_quality_score", "updated_at")
    list_filter = ("is_primary", "is_public")
    search_fields = ("title", "candidate__user__email")
    raw_id_fields = ("candidate",)
    inlines = [ExperienceInline, EducationInline, CVSkillInline]


# ─── Applications ─────────────────────────────

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job_offer", "status", "ai_match_score", "applied_at")
    list_filter = ("status",)
    search_fields = ("candidate__user__email", "job_offer__title")
    raw_id_fields = ("candidate", "job_offer", "cv")
    date_hierarchy = "applied_at"


# ─── Pricing & Subscriptions ─────────────────

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "target", "price", "duration_days", "has_ai_features", "is_active")
    list_filter = ("target", "is_active", "has_ai_features")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "starts_at", "expires_at", "amount_paid")
    list_filter = ("status", "plan")
    search_fields = ("user__email", "payment_reference")
    raw_id_fields = ("user",)


# ─── Alerts ───────────────────────────────────

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ("name", "candidate", "min_match_score", "is_active", "last_notified_at")
    list_filter = ("is_active",)
    search_fields = ("name", "candidate__user__email")
    raw_id_fields = ("candidate",)
