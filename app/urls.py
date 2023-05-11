from django.urls import path
from .views import get_pipeline_versions


urlpatterns = [
    path("get-pipeline-versions", get_pipeline_versions, name="getPipelineVersions"),
]
