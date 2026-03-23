from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("ai/api/jobs/", include("jobs.api.urls")),
    path("ai/api/", include("ai_engine.api.urls")),
    path("api/", include("jobs.api.user_urls")),
    path("api/ai/", include("ai_engine.api.assistant_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += []
