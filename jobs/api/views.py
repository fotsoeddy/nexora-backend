from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from jobs.api.serializers import JobOfferReadSerializer, JobOfferWriteSerializer
from jobs.models import JobOffer


class IsCompanyOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        company_profile = getattr(request.user, "company_profile", None)
        return company_profile is not None and obj.company_id == company_profile.id


class JobListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsCompanyOwnerOrReadOnly]
    lookup_field = "uuid"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        queryset = (
            JobOffer.objects.filter(is_active=True)
            .select_related("company", "domain")
            .prefetch_related("required_skills")
            .order_by("-created_at")
        )
        if self.request.method in permissions.SAFE_METHODS:
            return queryset
        company_profile = getattr(self.request.user, "company_profile", None)
        if company_profile is None:
            return JobOffer.objects.none()
        return queryset.filter(company=company_profile)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return JobOfferReadSerializer
        return JobOfferWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["company_profile"] = getattr(self.request.user, "company_profile", None)
        return context

    def perform_create(self, serializer):
        company_profile = getattr(self.request.user, "company_profile", None)
        if company_profile is None:
            raise PermissionDenied("A company profile is required to create a job.")
        serializer.save()


class JobRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCompanyOwnerOrReadOnly]
    lookup_field = "uuid"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return (
            JobOffer.objects.filter(is_active=True)
            .select_related("company", "domain")
            .prefetch_related("required_skills")
        )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return JobOfferReadSerializer
        return JobOfferWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["company_profile"] = getattr(self.request.user, "company_profile", None)
        return context

    def perform_destroy(self, instance):
        instance.soft_delete()
