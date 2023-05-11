from .views import researcher_view, get_pipeline_versions_to_ajax
from django.urls import path


urlpatterns = [
    path("researcher/requests", researcher_view, name="researcher"),
    path("researcher/get-pipeline-versions-to-ajax", get_pipeline_versions_to_ajax, name="getPipelineVersionsToAjax"),
]
