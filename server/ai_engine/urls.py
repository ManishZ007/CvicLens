from django.urls import path

from .views import classify, transcribe
from .nearby import duplicates, nearby

urlpatterns = [
    path("classify/", classify, name="ai-classify"),
    path("transcribe/", transcribe, name="ai-transcribe"),
    path("duplicates/", duplicates, name="ai-duplicates"),
    path("nearby/", nearby, name="nearby-complaints"),
]
