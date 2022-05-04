from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from filingcabinet.api_views import (
    DocumentCollectionViewSet,
    DocumentViewSet,
    PageAnnotationViewSet,
    PageViewSet,
)
from rest_framework.routers import DefaultRouter

from fcdocs_annotate.annotation.api import FeatureViewSet
from fcdocs_annotate.annotation.views import AnnotateDocumentView

api_router = DefaultRouter()
api_router.register(r"document", DocumentViewSet, basename="document")
api_router.register(
    r"documentcollection", DocumentCollectionViewSet, basename="documentcollection"
)
api_router.register(r"page", PageViewSet, basename="page")
api_router.register(r"pageannotation", PageAnnotationViewSet, basename="pageannotation")
api_router.register(r"feature", FeatureViewSet, basename="feature")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((api_router.urls, "api"))),
    path("document", include("filingcabinet.urls")),
    path("annotate/", AnnotateDocumentView.as_view(), name="document-detail"),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
