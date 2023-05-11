from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("", include("kubeflow_admin.urls")),
    path("", include("kubeflow_researcher.urls")),
    ] + static(settings.STATIC_URL_LOCAL, document_root=settings.STATIC_ROOT)
