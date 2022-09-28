from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Feature
from .serializers import FeatureSerializer, PredictionServiceSerializer
from .tasks import predict_feature_for_document_url


class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Feature.objects.all().prefetch_related(
        "fcdocs_annotation_featureannotation_annotations__document"
    )
    serializer_class = FeatureSerializer
    permission_classes = []

    @action(detail=True, methods=["post"])
    def predict(self, request, pk=None):
        feature = self.get_object()
        serializer = PredictionServiceSerializer(data=request.data)
        if serializer.is_valid():
            pending_task = predict_feature_for_document_url.delay(
                feature.id,
                serializer.validated_data["document_url"],
                serializer.validated_data["callback_url"],
            )
            return Response({"status": "pending", "task_id": str(pending_task.id)})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
