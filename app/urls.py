from django.urls import path
from .views import researcher_view, admin_view, add_run_request


urlpatterns = [
    path("add_run_request", add_run_request, name="add_run_request"),
    path("", researcher_view, name="researcher"),
    path("administrator", admin_view, name="admin"),

]
