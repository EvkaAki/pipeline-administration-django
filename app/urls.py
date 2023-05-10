from django.urls import path
from .views import researcher_view, admin_view, add_run_request


urlpatterns = [
    path("", researcher_view, name="researcher"),
    path("add_run_request", add_run_request, name="add_run_request"),
    path("administrator", admin_view, name="admin"),

]
