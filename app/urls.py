from django.urls import path

from .views import researcher_view

urlpatterns = [
    path("", researcher_view, name="researcher"),
]
