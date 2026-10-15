
from django.urls import path

from . import notification_views, views

urlpatterns = [
    path("csrf/", views.csrf_token, name="complaint-csrf"),
    path("", views.complaints, name="complaint-list-create"),
    path("<int:pk>/", views.complaint_detail, name="complaint-detail"),
    path(
        "media/<int:pk>/",
        views.complaint_media,
        name="complaint-media",
    ),
    path("routing-options/", views.routing_options, name="routing-options"),
    path("<int:pk>/status/", views.update_status, name="update-status"),
    path(
        "notifications/",
        notification_views.notifications,
        name="notifications",
    ),
    path(
        "notifications/<int:pk>/read/",
        notification_views.mark_read,
        name="notification-read",
    ),
]
