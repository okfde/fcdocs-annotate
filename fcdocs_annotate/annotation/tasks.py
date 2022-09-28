import logging
import tempfile

import requests
from celery import shared_task
from fcdocs_annotate.annotation.models import Feature
from filingcabinet import get_document_model

Document = get_document_model()
logger = logging.getLogger(__file__)


def get_prediction_module():
    try:
        from . import prediction
    except ImportError as e:
        logger.warn("Prediction not run, as dependencies not installed: %s", e)
        return None
    return prediction


@shared_task
def predict_feature_for_documents(feature_id, document_ids):
    prediction = get_prediction_module()
    if prediction is None:
        return
    try:
        feature = Feature.objects.get(id=feature_id)
    except Feature.DoesNotExist:
        return
    documents = Document.objects.filter(id__in=document_ids)
    prediction.create_feature_annotations(feature, documents)


@shared_task(bind=True)
def predict_feature_for_document_url(self, feature_id, document_url, callback_url):
    """
    Download file to temporary file with requests, predict feature
    and send result back to webhook callback URL.
    """
    data = {
        "feature_id": feature_id,
        "document_url": document_url,
        "callback_url": callback_url,
        "task_id": str(self.request.id),
        "result": None,
    }
    prediction = get_prediction_module()
    if prediction is None:
        _post_result(
            data, "aborted", "Prediction not run, as dependencies are not installed"
        )
        return
    try:
        feature = Feature.objects.get(id=feature_id)
    except Feature.DoesNotExist:
        _post_result(data, "aborted", "Feature does not exist")
        return

    try:
        with prediction.get_prediction_model(feature.model_path.path) as model:
            with tempfile.NamedTemporaryFile() as tmp_file:
                response = requests.get(document_url, stream=True)
                for chunk in response.iter_content(chunk_size=128):
                    tmp_file.write(chunk)
                tmp_file.flush()
                data["result"] = prediction.run_classification(model, tmp_file.name)
    except Exception as e:
        logger.exception(e)
        _post_result(data, "failed", str(e))
        return
    _post_result(data, "complete")


def _post_result(data, status, details=""):
    data["status"] = status
    data["details"] = details
    requests.post(data["callback_url"], json=data)
