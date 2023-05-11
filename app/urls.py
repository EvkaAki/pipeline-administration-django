from django.urls import path
from .views import get_pipeline_versions, get_view


urlpatterns = [
    path("get-pipeline-versions", get_pipeline_versions, name="getPipelineVersions"),
    path("", get_view, name="get_view"),
]
