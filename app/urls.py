from django.urls import path
from .views import get_pipeline_versions_by_id, get_view, download_artefact_view


urlpatterns = [
    path("get-pipeline-versions", get_pipeline_versions_by_id, name="getPipelineVersions"),
    path("", get_view, name="getView"),
    path('researcher/download-artefact', download_artefact_view, name='download_artefact'),
    path('administrator/download-artefact', download_artefact_view, name='download_artefact_admin'),
]
