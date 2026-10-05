from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.csrf_token),
    path("", views.complaints),
    path("media/<int:pk>/", views.complaint_media),
    path("<int:pk>/", views.complaint_detail),
]