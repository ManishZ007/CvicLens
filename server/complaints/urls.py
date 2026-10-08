from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.csrf_token),
    path("routing-options/", views.routing_options),
    path("", views.complaints),
    path("media/<int:pk>/", views.complaint_media),
    path("<int:pk>/", views.complaint_detail),
    path("<int:pk>/status/", views.update_status),
]