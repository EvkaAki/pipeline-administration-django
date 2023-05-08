from django.urls import path

from .views import researcher_view, admin_view

urlpatterns = [
    path("", researcher_view, name="researcher"),
    path("administrator", admin_view, name="admin"),
]
