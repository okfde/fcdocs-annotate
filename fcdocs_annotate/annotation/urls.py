from django.urls import path

from .views import AnnotateDocumentView, AnnotationsOverviewView, predict_feature

urlpatterns = [
    path("", AnnotationsOverviewView.as_view()),
    path("annotate/", AnnotateDocumentView.as_view(), name="annotate-document"),
    path("predict/<int:feature_id>/", predict_feature, name="annotate-predict_feature"),
]
