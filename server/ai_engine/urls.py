from django.urls import path

from .views import classify, transcribe

urlpatterns = [
    path("classify/", classify, name="ai-classify"),
    path("transcribe/", transcribe, name="ai-transcribe"),
]
