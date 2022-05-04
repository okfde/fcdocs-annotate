from rest_framework import serializers

from .models import Feature


class FeatureSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = ["id", "name", "question", "description", "documents"]

    def get_documents(self, object):
        true_annotations = object.feature_annotations.filter(value=True)
        false_annotations = object.feature_annotations.filter(value=False)
        return {
            "true": true_annotations.values_list("document", flat=True),
            "false": false_annotations.values_list("document", flat=True),
        }
