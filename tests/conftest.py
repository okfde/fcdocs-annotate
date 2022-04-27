import pytest
from pytest_factoryboy import register

from tests.factories import (
    DocumentFactory,
    FeatureAnnotationDraftFactory,
    FeatureAnnotationFactory,
    FeatureFactory,
)

register(DocumentFactory)
register(FeatureFactory)
register(FeatureAnnotationFactory)
register(FeatureAnnotationDraftFactory)


@pytest.fixture
def formset_data():
    def make_formset_data(formdata):
        formset_data = {
            "form-TOTAL_FORMS": ["2"],
            "form-INITIAL_FORMS": ["2"],
            "form-MIN_NUM_FORMS": ["0"],
            "form-MAX_NUM_FORMS": ["1000"],
        }

        for index, data in enumerate(formdata):
            feature_id = data[0]
            document_id = data[1]
            value = data[2]

            form_value = "form-{}-value".format(index)
            form_document = "form-{}-document".format(index)
            form_feature = "form-{}-feature".format(index)

            formset_data[form_value] = value
            formset_data[form_feature] = feature_id
            formset_data[form_document] = document_id

        return formset_data

    return make_formset_data


@pytest.fixture
def get_documents():
    def make_documents(number):
        documents = []
        for _i in range(number):
            documents.append(DocumentFactory(public=True))
        return tuple(documents)

    return make_documents


@pytest.fixture
def get_features():
    def make_features(number, documents_needed=None):
        features = []
        for _i in range(number):
            if not documents_needed:
                features.append(FeatureFactory())
            else:
                features.append(FeatureFactory(documents_needed=documents_needed))
        return tuple(features)

    return make_features


@pytest.fixture
def get_annotation_drafts():
    def make_annotation_drafts(number, documents, features, session):
        if hasattr(session, "session_key"):
            session = session.session_key
        annotations = []
        for i in range(number):
            for feature in features:
                annotations.append(
                    FeatureAnnotationDraftFactory(
                        document=documents[i], feature=feature, session=session
                    )
                )
        return tuple(annotations)

    return make_annotation_drafts


@pytest.fixture
def get_annotations():
    def make_annotations(number, documents, features):
        annotations = []
        for i in range(number):
            for feature in features:
                annotations.append(
                    FeatureAnnotationFactory(document=documents[i], feature=feature)
                )
        return tuple(annotations)

    return make_annotations
