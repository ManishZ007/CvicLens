
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("me/", views.current_user_view, name="current-user"),
    path("preferences/", views.preferences_view, name="preferences"),
    path("logout/", views.logout_view, name="logout"),
]
