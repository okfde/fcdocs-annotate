import pytest
from annotation.models import Feature, FeatureAnnotation


@pytest.mark.django_db
@pytest.mark.parametrize(
    "document_count, answered_documents, progress",
    [
        (3, 0, 0),
        (100, 0, 0),
        (3, 1, 33),
        (4, 1, 25),
        (5, 1, 20),
        (6, 1, 16),
        (100, 1, 1),
        (3, 3, 100),
        (100, 100, 100),
    ],
)
def test_annotate_view_get(
    client,
    get_documents,
    get_features,
    document_count,
    get_annotations,
    answered_documents,
    progress,
):

    session = client.session
    features = get_features(2)
    documents = get_documents(document_count)
    get_annotations(answered_documents, documents, features, session)
    annotated_documents = Feature.objects.documents_done_by_user(session).values_list(
        "id", flat=True
    )

    assert len(annotated_documents) == answered_documents

    try:
        documents_without_annotation = [
            d for d in documents if d.id not in annotated_documents
        ]
        document = documents_without_annotation[0]
    except IndexError:
        document = None

    response = client.get("/annotate/")
    assert response.context_data.get("object") == document
    assert response.context_data.get("progress") == progress
    if answered_documents < document_count:
        formset = response.context_data.get("feature_form_set")
        assert len(formset.initial) == 2
    else:
        assert not response.context_data.get("feature_form_set")


@pytest.mark.django_db
def test_annotate_view_post(get_documents, get_features, formset_data, client):
    d1, d2, d3 = get_documents(3)
    f1, f2 = get_features(2)
    f1.documents_needed = 1
    f1.save()

    data = formset_data(formdata=[(f1.id, d1.id, True), (f2.id, d1.id, False)])
    response = client.post("/annotate/", data, follow=True)
    assert response.context_data.get("object") == d2
    for entry in response.context_data.get("feature_form_set").initial:
        assert entry.get("document") == d2.id
        assert entry.get("feature") in [f1.id, f2.id]

    data = formset_data(formdata=[(f1.id, d2.id, False), (f2.id, d2.id, True)])

    response = client.post("/annotate/", data, follow=True)
    assert response.context_data.get("object") == d3
    for entry in response.context_data.get("feature_form_set").initial:
        assert entry.get("document") == d3.id
        assert entry.get("feature") in [f1.id, f2.id]

    data = formset_data(formdata=[(f1.id, d3.id, True), (f2.id, d3.id, True)])

    response = client.post("/annotate/", data, follow=True)
    assert not response.context_data.get("object")
    assert response.context_data.get("progress") == 100
    assert not response.context_data.get("feature_form_set")

    assert FeatureAnnotation.objects.filter(final=True).count() == 0
    assert Feature.objects.annotation_needed().count() == 2


@pytest.mark.django_db
def test_annotate_view_clear_session_after_feature_added(
    get_documents, get_features, get_annotations, client
):
    documents = get_documents(3)
    features = get_features(1)
    session = client.session
    session.save()

    get_annotations(2, documents, features, session, final=True)

    assert Feature.objects.documents_for_annotation().count() == 1

    response = client.get("/annotate/")
    assert response.context_data.get("object") == documents[-1]
    assert response.context_data.get("progress") == 0
    assert len(response.context_data.get("feature_form_set").initial) == 1

    get_features(1)

    response = client.get("/annotate/")
    assert response.context_data.get("object") == documents[0]
    assert response.context_data.get("progress") == 0
    formset = response.context_data.get("feature_form_set")
    assert len(formset.initial) == 1
