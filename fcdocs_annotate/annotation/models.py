import collections

from django.db import models
from django.utils.translation import gettext_lazy as _
from filingcabinet import get_document_model

Document = get_document_model()

TYPE_MANUAL = "TM"
TYPE_AUTOMATED = "TA"
FEATURE_ANNOTATION_TYPES = [
    (TYPE_MANUAL, _("Manual Annotation")),
    (TYPE_AUTOMATED, _("Automated Annotations")),
]


class Feature(models.Model):
    name = models.CharField(max_length=500)
    question = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    documents_needed = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name


class FeatureAnnotation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    features = models.JSONField(default=dict)
    type = models.CharField(
        max_length=2,
        choices=FEATURE_ANNOTATION_TYPES,
        default=TYPE_MANUAL,
    )
    final = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.final and self.type == TYPE_MANUAL:
            self.final, self.features = self.check_final()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.document.title

    def get_all_annotations(self):
        return self.document.featureannotation_set.filter(type=TYPE_MANUAL)

    def check_final(self):
        annotations = self.get_all_annotations()
        if annotations.count() == 1:
            final = annotations.first().features == self.features
            return final, self.features
        elif annotations.count() > 1:
            features_list = [a.features for a in annotations] + [self.features]
            features = self.merge_features(features_list)
            annotations.delete()
            return True, features
        return False, self.features

    def merge_features(self, feature_list):
        super_dict = collections.defaultdict(list)
        for feature in feature_list:
            for k, v in feature.items():
                super_dict[k].append(v)
        result_dict = {}
        for k, v in super_dict.items():
            c = collections.Counter(v)
            value, count = c.most_common()[0]
            result_dict[k] = value
        return result_dict
