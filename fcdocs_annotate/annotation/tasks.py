import logging
import tempfile

import requests
from celery import shared_task
from fcdocs_annotate.annotation.models import Feature
from filingcabinet import get_document_model

Document = get_document_model()
logger = logging.getLogger(__file__)


@shared_task
def predict_feature_for_documents(feature_id, document_ids):
    try:
        from .prediction import create_feature_annotations
    except ImportError:
        logger.warn("Prediction not run, as dependencies not installed")
        return None

    try:
        feature = Feature.objects.get(id=feature_id)
    except Feature.DoesNotExist:
        return
    documents = Document.objects.filter(id__in=document_ids)
    create_feature_annotations(feature, documents)


@shared_task
def predict_feature_for_document_url(feature_id, document_url, callback_url):
    """
    Download file to temporary file with requests, predict feature
    and send result back to webhook callback URL.
    """
    try:
        from .prediction import get_prediction_model, run_classification
    except ImportError:
        logger.warn("Prediction not run, as dependencies not installed")
        return None

    try:
        feature = Feature.objects.get(id=feature_id)
    except Feature.DoesNotExist:
        return

    with get_prediction_model(feature.model_path) as model:
        with tempfile.NamedTemporaryFile() as tmp_file:
            response = requests.get(document_url, stream=True)
            for chunk in response.iter_content(chunk_size=128):
                tmp_file.write(chunk)
            tmp_file.flush()
            result = run_classification(model, tmp_file.name)
            requests.post(callback_url, json={"result": result})
