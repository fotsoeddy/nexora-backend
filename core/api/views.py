from collections import Counter
from datetime import timedelta
from hashlib import sha1

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.models import (
    Application,
    AssistantChatMessage,
    AssistantChatSession,
    CoverLetterDraft,
    InterviewSession,
    Job,
    JobAlert,
    SalaryEstimate,
    SavedJob,
)
from core.api.serializers import (
    AdminApplicationSerializer,
    AdminApplicationUpdateSerializer,
    AdminCompanySerializer,
    AdminCompanyUpdateSerializer,
    AdminDashboardSerializer,
    AdminInterviewSerializer,
    AdminInterviewUpdateSerializer,
    AdminJobAlertSerializer,
    AdminJobAlertUpdateSerializer,
    AdminJobSerializer,
    AdminOperationsSerializer,
    AdminPublicationSerializer,
    AdminPublicationUpdateSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
)


class AdminOnlyPermission(permissions.IsAdminUser):
    """Dedicated permission class for staff-only dashboard access."""


def _build_daily_series(queryset, field_name, days=7):
    today = timezone.now().date()
    start_date = today - timedelta(days=days - 1)
    counts = {
        item["bucket"]: item["total"]
        for item in queryset.filter(**{f"{field_name}__date__gte": start_date})
        .annotate(bucket=TruncDate(field_name))
        .values("bucket")
        .annotate(total=Count("id"))
    }
    return [
        {
            "label": (start_date + timedelta(days=index)).strftime("%d %b"),
            "value": counts.get(start_date + timedelta(days=index), 0),
        }
        for index in range(days)
    ]


def _metric(label, queryset, field_name):
    now = timezone.now()
    current_start = now - timedelta(days=30)
    previous_start = now - timedelta(days=60)
    current_value = queryset.filter(**{f"{field_name}__gte": current_start}).count()
    previous_value = queryset.filter(
        **{f"{field_name}__gte": previous_start, f"{field_name}__lt": current_start}
    ).count()
    return {
        "label": label,
        "value": queryset.count(),
        "delta": current_value - previous_value,
    }


def _company_key(company_name):
    normalized = (company_name or "Unknown company").strip()
    return sha1(normalized.encode("utf-8")).hexdigest()[:16]


def _resolve_company_name(company_key):
    company_names = (
        Job.objects.exclude(company_name__isnull=True)
        .exclude(company_name="")
        .values_list("company_name", flat=True)
        .distinct()
    )
    for company_name in company_names:
        if _company_key(company_name) == company_key:
            return company_name
    return None


@extend_schema(tags=["Admin"], responses=AdminDashboardSerializer)
class AdminDashboardView(APIView):
    permission_classes = [AdminOnlyPermission]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        jobs = Job.objects.all()
        applications = Application.objects.all()
        interviews = InterviewSession.objects.all()

        jobs_by_type = Counter(
            jobs.exclude(employment_type__isnull=True)
            .exclude(employment_type="")
            .values_list("employment_type", flat=True)
        )
        application_funnel = Counter(applications.values_list("status", flat=True))
        interview_statuses = Counter(interviews.values_list("interview_status", flat=True))
        publication_health = Counter("active" if job.status == 1 else "inactive" for job in jobs)
        top_companies = (
            jobs.exclude(company_name__isnull=True)
            .exclude(company_name="")
            .values("company_name")
            .annotate(total=Count("id"))
            .order_by("-total", "company_name")[:6]
        )

        ai_usage = [
            {"label": "Chat sessions", "value": AssistantChatSession.objects.count()},
            {"label": "Chat messages", "value": AssistantChatMessage.objects.count()},
            {"label": "Cover letters", "value": CoverLetterDraft.objects.count()},
            {"label": "Salary estimates", "value": SalaryEstimate.objects.count()},
            {"label": "Alerts", "value": JobAlert.objects.count()},
        ]

        recent_activity = []

        for user in users.order_by("-date_joined")[:3]:
            recent_activity.append(
                {
                    "id": f"user-{user.pk}",
                    "type": "user",
                    "title": user.get_full_name().strip() or user.username,
                    "subtitle": f"New account registered with {user.email}",
                    "timestamp": user.date_joined,
                }
            )

        for job in jobs.order_by("-created")[:3]:
            recent_activity.append(
                {
                    "id": f"job-{job.pk}",
                    "type": "job",
                    "title": job.title,
                    "subtitle": f"{job.company_name or 'Unknown company'} posted a role",
                    "timestamp": job.created,
                }
            )

        for application in applications.select_related("job", "user").order_by("-applied_at")[:4]:
            recent_activity.append(
                {
                    "id": f"application-{application.pk}",
                    "type": "application",
                    "title": application.job.title,
                    "subtitle": f"{application.user.email} applied",
                    "timestamp": application.applied_at,
                }
            )

        for session in interviews.select_related("user", "job").order_by("-created")[:4]:
            recent_activity.append(
                {
                    "id": f"interview-{session.pk}",
                    "type": "interview",
                    "title": session.job.title if session.job_id else (session.target_job_title or "Interview"),
                    "subtitle": f"{session.user.email} session is {session.interview_status}",
                    "timestamp": session.created,
                }
            )

        recent_activity.sort(key=lambda item: item["timestamp"], reverse=True)

        payload = {
            "metrics": [
                _metric("Users", users, "date_joined"),
                _metric("Jobs", jobs, "created"),
                _metric("Applications", applications, "applied_at"),
                _metric("Interviews", interviews, "created"),
            ],
            "user_growth": _build_daily_series(users, "date_joined"),
            "application_growth": _build_daily_series(applications, "applied_at"),
            "jobs_by_type": [
                {"label": key.replace("_", " ").title(), "value": value}
                for key, value in sorted(jobs_by_type.items())
            ],
            "application_funnel": [
                {"label": key.replace("_", " ").title(), "value": value}
                for key, value in sorted(application_funnel.items())
            ],
            "interview_statuses": [
                {"label": key.replace("_", " ").title(), "value": value}
                for key, value in sorted(interview_statuses.items())
            ],
            "ai_usage": ai_usage,
            "publication_health": [
                {"label": key.title(), "value": value}
                for key, value in sorted(publication_health.items())
            ],
            "top_companies": [
                {"label": item["company_name"], "value": item["total"]}
                for item in top_companies
            ],
            "recent_activity": recent_activity[:8],
        }
        serializer = AdminDashboardSerializer(payload)
        return Response(serializer.data)


@extend_schema(tags=["Admin"], responses=AdminUserSerializer(many=True))
class AdminUserListView(generics.ListAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        queryset = User.objects.annotate(
            applications_count=Count("applications", distinct=True),
            saved_jobs_count=Count("saved_jobs", distinct=True),
            alerts_count=Count("job_alerts", distinct=True),
            interview_sessions_count=Count("interview_sessions", distinct=True),
            assistant_sessions_count=Count("assistant_chat_sessions", distinct=True),
        ).order_by("-date_joined")
        search = self.request.query_params.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        if self.request.query_params.get("verified") == "true":
            queryset = queryset.filter(is_active=True)
        if self.request.query_params.get("staff") == "true":
            queryset = queryset.filter(is_staff=True)
        return queryset


@extend_schema(tags=["Admin"], responses=AdminUserSerializer, request=AdminUserUpdateSerializer)
class AdminUserDetailView(APIView):
    permission_classes = [AdminOnlyPermission]

    def patch(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.annotate(
            applications_count=Count("applications", distinct=True),
            saved_jobs_count=Count("saved_jobs", distinct=True),
            alerts_count=Count("job_alerts", distinct=True),
            interview_sessions_count=Count("interview_sessions", distinct=True),
            assistant_sessions_count=Count("assistant_chat_sessions", distinct=True),
        ).get(pk=user.pk)
        return Response(AdminUserSerializer(user).data)


@extend_schema(tags=["Admin"], responses=AdminJobSerializer(many=True))
class AdminJobListCreateView(generics.ListCreateAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = AdminJobSerializer

    def get_queryset(self):
        queryset = Job.objects.select_related("created_by").annotate(
            applications_count=Count("applications", distinct=True),
            interview_sessions_count=Count("interview_sessions", distinct=True),
        ).order_by("-created")
        search = self.request.query_params.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(company_name__icontains=search)
                | Q(location__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema(tags=["Admin"], responses=AdminJobSerializer, request=AdminJobSerializer)
class AdminJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = AdminJobSerializer

    def get_queryset(self):
        return Job.objects.select_related("created_by").annotate(
            applications_count=Count("applications", distinct=True),
            interview_sessions_count=Count("interview_sessions", distinct=True),
        )


@extend_schema(tags=["Admin"], responses=AdminApplicationSerializer(many=True))
class AdminApplicationListView(generics.ListAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = AdminApplicationSerializer

    def get_queryset(self):
        queryset = Application.objects.select_related("user", "job").order_by("-applied_at")
        search = self.request.query_params.get("q", "").strip()
        status_filter = self.request.query_params.get("status", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search)
                | Q(job__title__icontains=search)
                | Q(job__company_name__icontains=search)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


@extend_schema(tags=["Admin"], responses=AdminApplicationSerializer, request=AdminApplicationUpdateSerializer)
class AdminApplicationDetailView(APIView):
    permission_classes = [AdminOnlyPermission]

    def patch(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Application.objects.select_related("user", "job"), pk=pk)
        serializer = AdminApplicationUpdateSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminApplicationSerializer(application).data)


@extend_schema(tags=["Admin"], responses=AdminInterviewSerializer(many=True))
class AdminInterviewListView(generics.ListAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = AdminInterviewSerializer

    def get_queryset(self):
        queryset = InterviewSession.objects.select_related("user", "job", "assistant", "feedback").order_by("-created")
        search = self.request.query_params.get("q", "").strip()
        status_filter = self.request.query_params.get("status", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search)
                | Q(job__title__icontains=search)
                | Q(target_job_title__icontains=search)
            )
        if status_filter:
            queryset = queryset.filter(interview_status=status_filter)
        return queryset


@extend_schema(tags=["Admin"], responses=AdminInterviewSerializer, request=AdminInterviewUpdateSerializer)
class AdminInterviewDetailView(APIView):
    permission_classes = [AdminOnlyPermission]

    def patch(self, request, pk, *args, **kwargs):
        session = get_object_or_404(
            InterviewSession.objects.select_related("user", "job", "assistant", "feedback"),
            pk=pk,
        )
        serializer = AdminInterviewUpdateSerializer(session, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminInterviewSerializer(session).data)


@extend_schema(tags=["Admin"], responses=AdminCompanySerializer(many=True))
class AdminCompanyListView(APIView):
    permission_classes = [AdminOnlyPermission]

    def get(self, request, *args, **kwargs):
        search = request.query_params.get("q", "").strip().lower()
        company_rows = (
            Job.objects.exclude(company_name__isnull=True)
            .exclude(company_name="")
            .values("company_name")
            .annotate(
                total_publications=Count("id"),
                active_publications=Count("id", filter=Q(status=1)),
                inactive_publications=Count("id", filter=Q(status=0)),
                applications_count=Count("applications", distinct=True),
                interview_sessions_count=Count("interview_sessions", distinct=True),
            )
            .order_by("company_name")
        )

        payload = []
        for row in company_rows:
            company_name = row["company_name"]
            if search and search not in company_name.lower():
                continue
            company_jobs = Job.objects.filter(company_name=company_name).order_by("-created")
            primary_locations = list(
                company_jobs.exclude(location__isnull=True)
                .exclude(location="")
                .values_list("location", flat=True)
                .distinct()[:3]
            )
            payload.append(
                {
                    "id": _company_key(company_name),
                    "company_name": company_name,
                    "active_publications": row["active_publications"],
                    "inactive_publications": row["inactive_publications"],
                    "total_publications": row["total_publications"],
                    "applications_count": row["applications_count"],
                    "interview_sessions_count": row["interview_sessions_count"],
                    "latest_publication_at": company_jobs.first().created if company_jobs.exists() else None,
                    "primary_locations": primary_locations,
                }
            )
        return Response(AdminCompanySerializer(payload, many=True).data)


@extend_schema(tags=["Admin"], responses=AdminCompanySerializer, request=AdminCompanyUpdateSerializer)
class AdminCompanyDetailView(APIView):
    permission_classes = [AdminOnlyPermission]

    def patch(self, request, company_key, *args, **kwargs):
        company_name = _resolve_company_name(company_key)
        if not company_name:
            return Response({"detail": "Company not found."}, status=404)

        serializer = AdminCompanyUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        jobs = Job.objects.filter(company_name=company_name)
        next_name = serializer.validated_data.get("company_name")
        publication_status = serializer.validated_data.get("publication_status")

        if next_name:
            jobs.update(company_name=next_name)
            company_name = next_name
            jobs = Job.objects.filter(company_name=company_name)

        if publication_status:
            jobs.update(status=1 if publication_status == "active" else 0)

        company_jobs = jobs.order_by("-created")
        payload = {
            "id": _company_key(company_name),
            "company_name": company_name,
            "active_publications": jobs.filter(status=1).count(),
            "inactive_publications": jobs.filter(status=0).count(),
            "total_publications": jobs.count(),
            "applications_count": Application.objects.filter(job__company_name=company_name).count(),
            "interview_sessions_count": InterviewSession.objects.filter(job__company_name=company_name).count(),
            "latest_publication_at": company_jobs.first().created if company_jobs.exists() else None,
            "primary_locations": list(
                company_jobs.exclude(location__isnull=True)
                .exclude(location="")
                .values_list("location", flat=True)
                .distinct()[:3]
            ),
        }
        return Response(AdminCompanySerializer(payload).data)


@extend_schema(tags=["Admin"], responses=AdminPublicationSerializer(many=True))
class AdminPublicationListView(generics.ListAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = AdminPublicationSerializer

    def get_queryset(self):
        queryset = Job.objects.select_related("created_by").annotate(
            applications_count=Count("applications", distinct=True),
            interview_sessions_count=Count("interview_sessions", distinct=True),
        ).order_by("-created")
        search = self.request.query_params.get("q", "").strip()
        status_filter = self.request.query_params.get("status", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(company_name__icontains=search)
                | Q(location__icontains=search)
            )
        if status_filter == "active":
            queryset = queryset.filter(status=1)
        elif status_filter == "inactive":
            queryset = queryset.filter(status=0)
        return queryset


@extend_schema(tags=["Admin"], responses=AdminPublicationSerializer, request=AdminPublicationUpdateSerializer)
class AdminPublicationDetailView(APIView):
    permission_classes = [AdminOnlyPermission]

    def patch(self, request, pk, *args, **kwargs):
        publication = get_object_or_404(
            Job.objects.select_related("created_by").annotate(
                applications_count=Count("applications", distinct=True),
                interview_sessions_count=Count("interview_sessions", distinct=True),
            ),
            pk=pk,
        )
        serializer = AdminPublicationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        publication.status = 1 if serializer.validated_data["publication_status"] == "active" else 0
        publication.save(update_fields=["status", "modified"])
        publication = Job.objects.select_related("created_by").annotate(
            applications_count=Count("applications", distinct=True),
            interview_sessions_count=Count("interview_sessions", distinct=True),
        ).get(pk=publication.pk)
        return Response(AdminPublicationSerializer(publication).data)

    def delete(self, request, pk, *args, **kwargs):
        publication = get_object_or_404(Job, pk=pk)
        publication.delete()
        return Response(status=204)


@extend_schema(tags=["Admin"], responses=AdminOperationsSerializer)
class AdminOperationsView(APIView):
    permission_classes = [AdminOnlyPermission]

    def get(self, request, *args, **kwargs):
        alerts = JobAlert.objects.select_related("user").order_by("-updated_at")[:10]
        saved_jobs = SavedJob.objects.select_related("user", "job").order_by("-created_at")[:10]
        assistant_sessions = AssistantChatSession.objects.select_related("user").order_by("-updated_at")[:10]
        cover_letters = CoverLetterDraft.objects.select_related("user", "job").order_by("-created_at")[:10]
        salary_estimates = SalaryEstimate.objects.select_related("user").order_by("-created_at")[:10]

        payload = {
            "metrics": [
                {"label": "Active alerts", "value": JobAlert.objects.filter(is_active=True).count()},
                {"label": "Saved jobs", "value": SavedJob.objects.count()},
                {"label": "AI chat sessions", "value": AssistantChatSession.objects.count()},
                {"label": "Cover letters", "value": CoverLetterDraft.objects.count()},
                {"label": "Salary estimates", "value": SalaryEstimate.objects.count()},
            ],
            "alerts": [
                {
                    "id": alert.id,
                    "user_email": alert.user.email,
                    "name": alert.name,
                    "keywords": alert.keywords,
                    "frequency": alert.frequency,
                    "is_active": alert.is_active,
                    "notify_by_email": alert.notify_by_email,
                    "notify_by_push": alert.notify_by_push,
                    "updated_at": alert.updated_at,
                }
                for alert in alerts
            ],
            "saved_jobs": [
                {
                    "id": str(saved_job.id),
                    "user_email": saved_job.user.email,
                    "job_title": saved_job.job.title,
                    "company_name": saved_job.job.company_name,
                    "created_at": saved_job.created_at,
                }
                for saved_job in saved_jobs
            ],
            "assistant_sessions": [
                {
                    "id": str(session.id),
                    "user_email": session.user.email,
                    "title": session.title,
                    "context_type": session.context_type,
                    "messages_count": session.messages_count,
                    "updated_at": session.updated_at,
                }
                for session in assistant_sessions
            ],
            "cover_letters": [
                {
                    "id": str(draft.id),
                    "user_email": draft.user.email,
                    "job_title": draft.job_title,
                    "company_name": draft.company_name,
                    "tone": draft.tone,
                    "created_at": draft.created_at,
                }
                for draft in cover_letters
            ],
            "salary_estimates": [
                {
                    "id": str(item.id),
                    "user_email": item.user.email,
                    "job_title": item.job_title,
                    "city": item.city,
                    "experience_level": item.experience_level,
                    "estimated_median": item.estimated_median,
                    "created_at": item.created_at,
                }
                for item in salary_estimates
            ],
        }
        return Response(AdminOperationsSerializer(payload).data)


@extend_schema(tags=["Admin"], responses=AdminJobAlertSerializer, request=AdminJobAlertUpdateSerializer)
class AdminJobAlertDetailView(APIView):
    permission_classes = [AdminOnlyPermission]

    def patch(self, request, pk, *args, **kwargs):
        alert = get_object_or_404(JobAlert.objects.select_related("user"), pk=pk)
        serializer = AdminJobAlertUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(alert, field, value)
        alert.save(update_fields=[*serializer.validated_data.keys(), "updated_at"])
        payload = {
            "id": alert.id,
            "user_email": alert.user.email,
            "name": alert.name,
            "keywords": alert.keywords,
            "frequency": alert.frequency,
            "is_active": alert.is_active,
            "notify_by_email": alert.notify_by_email,
            "notify_by_push": alert.notify_by_push,
            "updated_at": alert.updated_at,
        }
        return Response(AdminJobAlertSerializer(payload).data)
