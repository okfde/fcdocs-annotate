from celery import shared_task
from fcdocs_annotate.annotation.models import Feature
from filingcabinet import get_document_model

Document = get_document_model()


@shared_task
def predict_feature_for_documents(feature_id, document_ids):
    try:
        feature = Feature.objects.get(id=feature_id)
        documents = Document.objects.filter(id__in=document_ids)
        if documents:
            return feature.predict(documents)
        return False
    except Feature.DoesNotExist:
        return False
