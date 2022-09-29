import os
import zipfile
from contextlib import contextmanager

import pandas as pd
from fcdocs.extras.datasets.document_dataset import DocumentDataSet
from fcdocs.pipelines.classifier.model_dataset import ModelDataSet

from .models import TYPE_AUTOMATED, FeatureAnnotation


def create_feature_annotations(feature, documents):
    with get_prediction_model(feature.model_path.path) as model:
        for doc in documents:
            prediction = run_classification(model, doc.pdf_file.path)
            FeatureAnnotation.objects.update_or_create(
                defaults={"document": doc, "feature": feature, "type": TYPE_AUTOMATED},
                value=True if prediction else False,
            )


def run_classification(model, pdf_file_path):
    document = DocumentDataSet(pdf_file_path).load()
    return bool(model.predict(pd.DataFrame([document]))[0][0])


@contextmanager
def get_prediction_model(model_path):
    if model_path.endswith(".zip"):
        # Unzip model if necessary
        real_model_path = model_path.replace(".zip", "/")
        if not os.path.exists(real_model_path):
            os.makedirs(real_model_path)
            with zipfile.ZipFile(model_path, "r") as zip_ref:
                zip_ref.extractall(real_model_path)
        model_path = real_model_path

    model = ModelDataSet(model_path, None).load()
    yield model
