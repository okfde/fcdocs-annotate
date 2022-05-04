from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Feature
from .serializers import FeatureSerializer


class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Feature.objects.all().prefetch_related(
        "fcdocs_annotation_featureannotation_annotations__document"
    )
    serializer_class = FeatureSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "name", "question"]
