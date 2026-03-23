from django.contrib.auth.models import User
from rest_framework import serializers

from ai.models import Application, InterviewSession, Job


class AdminMetricSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.IntegerField()
    delta = serializers.IntegerField()


class AdminSeriesPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.FloatField()


class AdminDistributionItemSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.IntegerField()


class AdminActivityItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField()
    timestamp = serializers.DateTimeField()


class AdminDashboardSerializer(serializers.Serializer):
    metrics = AdminMetricSerializer(many=True)
    user_growth = AdminSeriesPointSerializer(many=True)
    application_growth = AdminSeriesPointSerializer(many=True)
    jobs_by_type = AdminDistributionItemSerializer(many=True)
    application_funnel = AdminDistributionItemSerializer(many=True)
    interview_statuses = AdminDistributionItemSerializer(many=True)
    ai_usage = AdminDistributionItemSerializer(many=True)
    publication_health = AdminDistributionItemSerializer(many=True)
    top_companies = AdminDistributionItemSerializer(many=True)
    recent_activity = AdminActivityItemSerializer(many=True)


class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    applications_count = serializers.IntegerField(read_only=True)
    saved_jobs_count = serializers.IntegerField(read_only=True)
    alerts_count = serializers.IntegerField(read_only=True)
    interview_sessions_count = serializers.IntegerField(read_only=True)
    assistant_sessions_count = serializers.IntegerField(read_only=True)
    is_email_verified = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_email_verified",
            "date_joined",
            "last_login",
            "applications_count",
            "saved_jobs_count",
            "alerts_count",
            "interview_sessions_count",
            "assistant_sessions_count",
        )

    def get_full_name(self, obj):
        return obj.get_full_name().strip() or obj.username


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_active", "is_staff")


class AdminJobSerializer(serializers.ModelSerializer):
    applications_count = serializers.IntegerField(read_only=True)
    interview_sessions_count = serializers.IntegerField(read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "company_name",
            "description",
            "requirements",
            "employment_type",
            "location",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
            "applications_count",
            "interview_sessions_count",
        )
        read_only_fields = (
            "id",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
            "applications_count",
            "interview_sessions_count",
        )


class AdminApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company_name", read_only=True, allow_null=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "job",
            "job_title",
            "company_name",
            "status",
            "cover_letter",
            "recruiter_notes",
            "ats_score",
            "applied_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "job", "applied_at", "created_at", "updated_at")

    def get_user_name(self, obj):
        return obj.user.get_full_name().strip() or obj.user.username


class AdminApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("status", "recruiter_notes", "ats_score")


class AdminInterviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    assistant_name = serializers.CharField(source="assistant.name", read_only=True, allow_null=True)
    overall_score = serializers.SerializerMethodField()
    strengths = serializers.SerializerMethodField()
    improvements = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = InterviewSession
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "job",
            "job_title",
            "assistant_name",
            "session_type",
            "interview_type",
            "interview_status",
            "difficulty",
            "question_count",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
            "overall_score",
            "strengths",
            "improvements",
        )
        read_only_fields = (
            "id",
            "user",
            "job",
            "assistant_name",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
            "overall_score",
            "strengths",
            "improvements",
        )

    def get_user_name(self, obj):
        return obj.user.get_full_name().strip() or obj.user.username

    def get_job_title(self, obj):
        if obj.job_id:
            return obj.job.title
        return obj.target_job_title or "General interview"

    def get_overall_score(self, obj):
        if hasattr(obj, "feedback") and obj.feedback.overall_score is not None:
            return float(obj.feedback.overall_score) * 10
        return None

    def get_strengths(self, obj):
        if hasattr(obj, "feedback"):
            return obj.feedback.strengths
        return []

    def get_improvements(self, obj):
        if hasattr(obj, "feedback"):
            return obj.feedback.improvements
        return []


class AdminInterviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ("interview_status", "difficulty", "question_count")


class AdminCompanySerializer(serializers.Serializer):
    id = serializers.CharField()
    company_name = serializers.CharField()
    active_publications = serializers.IntegerField()
    inactive_publications = serializers.IntegerField()
    total_publications = serializers.IntegerField()
    applications_count = serializers.IntegerField()
    interview_sessions_count = serializers.IntegerField()
    latest_publication_at = serializers.DateTimeField(allow_null=True)
    primary_locations = serializers.ListField(child=serializers.CharField())


class AdminCompanyUpdateSerializer(serializers.Serializer):
    company_name = serializers.CharField(required=False, allow_blank=False, max_length=255)
    publication_status = serializers.ChoiceField(choices=("active", "inactive"), required=False)


class AdminPublicationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(read_only=True, allow_null=True)
    publication_status = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True, allow_null=True)
    applications_count = serializers.IntegerField(read_only=True)
    interview_sessions_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "company_name",
            "employment_type",
            "location",
            "publication_status",
            "created_by_email",
            "applications_count",
            "interview_sessions_count",
            "created_at",
            "updated_at",
        )

    def get_publication_status(self, obj):
        return "active" if obj.status == 1 else "inactive"


class AdminPublicationUpdateSerializer(serializers.Serializer):
    publication_status = serializers.ChoiceField(choices=("active", "inactive"))


class AdminJobAlertSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_email = serializers.EmailField()
    name = serializers.CharField()
    keywords = serializers.CharField()
    frequency = serializers.CharField()
    is_active = serializers.BooleanField()
    notify_by_email = serializers.BooleanField()
    notify_by_push = serializers.BooleanField()
    updated_at = serializers.DateTimeField()


class AdminJobAlertUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    notify_by_email = serializers.BooleanField(required=False)
    notify_by_push = serializers.BooleanField(required=False)


class AdminOperationsSerializer(serializers.Serializer):
    metrics = AdminDistributionItemSerializer(many=True)
    alerts = AdminJobAlertSerializer(many=True)
    saved_jobs = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    assistant_sessions = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    cover_letters = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    salary_estimates = serializers.ListField(child=serializers.DictField(), allow_empty=True)
