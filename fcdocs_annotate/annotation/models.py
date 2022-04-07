import collections
from typing import final
from django.db.models import Q, Count, F
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from filingcabinet import get_document_model

Document = get_document_model()

TYPE_MANUAL = "TM"
TYPE_AUTOMATED = "TA"
FEATURE_ANNOTATION_TYPES = [
    (TYPE_MANUAL, _("Manual Annotation")),
    (TYPE_AUTOMATED, _("Automated Annotations")),
]


class FeatureManager(models.Manager):

    def with_final_annotations_count(self):
        return self.annotate(
            final_annotations_count=Count(
                'feature_annotations',
                filter=(Q(feature_annotations__final=True) &
                        Q(feature_annotations__value=True) &
                        Q(feature_annotations__type=TYPE_MANUAL)))
        )

    def annotation_needed(self):
        return self.with_final_annotations_count().filter(
            final_annotations_count__lt=F('documents_needed'))

    def documents_for_annotation(self):
        feature_list = self.annotation_needed().values_list('id', flat=True)
        if feature_list:
            subquery = FeatureAnnotation.objects.filter(
                feature__in=feature_list, document=OuterRef("id"))
            return Document.objects.annotate(
                has_annotation=Exists(subquery)).order_by('-has_annotation')
        return Document.objects.none()


class Feature(models.Model):
    name = models.CharField(max_length=500)
    question = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    documents_needed = models.PositiveIntegerField(default=10)

    objects = FeatureManager()

    def __str__(self):
        return self.name

    def final_annotation_count(self):
        annotations = self.feature_annotations.filter(
            final=True,
            value=True,
            type=TYPE_MANUAL
        )
        return annotations.count()


class FeatureAnnotation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    features = models.JSONField(default=dict)
    type = models.CharField(
        max_length=2,
        choices=FEATURE_ANNOTATION_TYPES,
        default=TYPE_MANUAL,
    )
    final = models.BooleanField(default=False)
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, null=True, related_name='feature_annotations')
    value = models.BooleanField(null=True)

    def save(self, *args, **kwargs):
        if not self.final and self.type == TYPE_MANUAL:
            self.final, self.value = self.check_final()
        super().save(*args, **kwargs)

    def __str__(self):
        SHORTEN = 30
        title = '{} {}'.format(str(self.document.id), self.document.title)
        if len(title) > SHORTEN:
            return title[:SHORTEN] + '..'
        return title

    def get_other_annotations(self):
        return self.document.featureannotation_set.filter(
            feature=self.feature,
            type=TYPE_MANUAL)

    def check_final(self):
        annotations = self.get_other_annotations()
        if annotations.count() == 1:
            final = annotations.first().value == self.value
            if final:
                annotations.delete()
            return final, self.value
        elif annotations.count() > 1:
            value_list = [a.value for a in annotations] + [self.value]
            c = collections.Counter(value_list)
            value, count = c.most_common()[0]
            annotations.delete()
            return True, value
        return False, self.value
