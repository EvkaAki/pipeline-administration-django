from django.urls import path
from .views import admin_view, request_detail


urlpatterns = [
    path("administrator/requests", admin_view, name="admin_requests"),
    path("administrator/requests/<int:request_id>", request_detail, name="admin_request_detail"),
]
