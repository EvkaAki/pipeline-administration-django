from .views import researcher_view
from django.urls import path


urlpatterns = [
    path("researcher", researcher_view, name="researcher"),
]
