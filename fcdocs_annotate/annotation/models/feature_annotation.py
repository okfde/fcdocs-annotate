from django.db import models
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from filingcabinet import get_document_model

from .abstract_annotation import AbstractAnnotation, AbstractAnnotationManager

Document = get_document_model()


TYPE_MANUAL = "TM"
TYPE_AUTOMATED = "TA"
FEATURE_ANNOTATION_TYPES = [
    (TYPE_MANUAL, _("Manual Annotation")),
    (TYPE_AUTOMATED, _("Automated Annotations")),
]


class AnnotationDocumentsManager(AbstractAnnotationManager):
    def documents_with_annotations_ids(self):
        return (
            self.all().select_related("documents").values_list("document_id", flat=True)
        )

    def documents_with_annotations(self):
        return Document.objects.filter(
            public=True, id__in=self.documents_with_annotations_ids()
        )

    def documents_without_annotations(self):
        document_ids = self.all().values_list("document_id", flat=True)
        return Document.objects.exclude(id__in=document_ids)

    def documents_with_annotation_count(self):
        from .feature import Feature

        feature_ids = Feature.objects.annotation_needed().values_list("id", flat=True)
        subquery = self._get_subquery(
            {"type": TYPE_MANUAL, "feature_id__in": feature_ids}
        )
        return self.documents_with_annotations().annotate(
            final_count=Coalesce(subquery, 0)
        )

    def final_documents(self):
        from .feature import Feature

        feature_count = Feature.objects.annotation_needed().count()
        documents = self.documents_with_annotation_count()
        return documents.filter(final_count__gte=feature_count)

    def unfinished_documents(self):
        from .feature import Feature

        feature_count = Feature.objects.annotation_needed().count()
        documents = self.documents_with_annotation_count()
        return documents.exclude(final_count__gte=feature_count)


class FeatureAnnotation(AbstractAnnotation):
    type = models.CharField(
        max_length=2,
        choices=FEATURE_ANNOTATION_TYPES,
        default=TYPE_MANUAL,
    )
    score = models.FloatField(null=True)

    objects = AnnotationDocumentsManager()

    class Meta:
        unique_together = ("feature", "document")
