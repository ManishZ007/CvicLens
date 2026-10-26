from . import notification_views, completion_views

from django.urls import path

from . import views
from .manual_routing import update_routing

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
    path("<int:pk>/routing/", update_routing, name="update-routing"),

path("notifications/", notification_views.notifications, name="notifications"),
path("notifications/<int:pk>/read/", notification_views.mark_read, name="notification-read"),
path("<int:pk>/resolution-photo/", completion_views.resolution_photo, name="resolution-photo"),
path("<int:pk>/feedback/", completion_views.feedback, name="complaint-feedback"),
path("<int:pk>/reopen/", completion_views.reopen, name="complaint-reopen"),
path("analytics/", completion_views.analytics, name="complaint-analytics"),
]
