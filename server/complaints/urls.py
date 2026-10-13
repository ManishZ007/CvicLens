
from django.urls import path

from . import views

urlpatterns = [
    path("", views.complaints, name="complaint-list-create"),
    path("<int:pk>/", views.complaint_detail, name="complaint-detail"),
    path(
        "<int:pk>/media/<int:media_id>/",
        views.complaint_media,
        name="complaint-media",
    ),
    path("routing-options/", views.routing_options, name="routing-options"),
    path("<int:pk>/status/", views.update_status, name="update-status"),
]
