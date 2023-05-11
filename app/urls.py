from django.urls import path
from .views import researcher_view, admin_view, get_pipeline_versions


urlpatterns = [
    path("", researcher_view, name="researcher"),
    path("administrator", admin_view, name="admin"),
    path("get-pipeline-versions", get_pipeline_versions, name="getPipelineVersions"),
]
