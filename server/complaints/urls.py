from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.csrf_token, name="complaints-csrf"),
    path("", views.create_complaint, name="complaints-create"),
]