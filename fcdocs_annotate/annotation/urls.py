from django.urls import path

from .views import AnnotateDocumentView, AnnotationsOverviewView

urlpatterns = [
    path("", AnnotationsOverviewView.as_view()),
    path("annotate/", AnnotateDocumentView.as_view(), name="annotate-document"),
]
