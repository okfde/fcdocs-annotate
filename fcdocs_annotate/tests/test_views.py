import random

import pytest
from annotation.models import Feature, FeatureAnnotation


@pytest.mark.django_db
@pytest.mark.parametrize(
    "document_count, answered_documents, progress",
    [
        (3, 0, 0),
        (4, 0, 0),
        (5, 0, 0),
        (6, 0, 0),
        (100, 0, 0),
        (3, 1, 33),
        (4, 1, 25),
        (5, 1, 20),
        (6, 1, 16),
        (100, 1, 1),
        (3, 3, 100),
    ],
)
def test_annotate_view_get(
    client, get_documents, get_features, document_count, answered_documents, progress
):

    documents = get_documents(document_count)
    annotated_documents = random.sample(documents, answered_documents)
    try:
        document = [d for d in documents if d not in annotated_documents][0]
    except IndexError:
        document = None
    get_features(2)

    session = client.session
    session["annotated_documents"] = [d.id for d in annotated_documents]
    session.save()

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
    assert client.session["annotated_documents"] == [d1.id]

    data = formset_data(formdata=[(f1.id, d2.id, False), (f2.id, d2.id, True)])

    response = client.post("/annotate/", data, follow=True)
    assert response.context_data.get("object") == d3
    for entry in response.context_data.get("feature_form_set").initial:
        assert entry.get("document") == d3.id
        assert entry.get("feature") in [f1.id, f2.id]
    assert client.session["annotated_documents"] == [d1.id, d2.id]

    data = formset_data(formdata=[(f1.id, d3.id, True), (f2.id, d3.id, True)])

    response = client.post("/annotate/", data, follow=True)
    assert not response.context_data.get("object")
    assert response.context_data.get("progress") == 100
    assert not response.context_data.get("feature_form_set")
    assert client.session["annotated_documents"] == [d1.id, d2.id, d3.id]

    assert FeatureAnnotation.objects.filter(final=True).count() == 0
    assert Feature.objects.annotation_needed().count() == 2

    session = client.session
    session["annotated_documents"] = [d1.id, d2.id]
    session.save()

    assert session["annotated_documents"] == [d1.id, d2.id]

    response = client.get("/annotate/")
    assert response.context_data.get("object") == d3
    assert response.context_data.get("progress") == 66

    data = formset_data(formdata=[(f1.id, d3.id, True), (f2.id, d3.id, True)])
    response = client.post("/annotate/", data, follow=True)

    assert FeatureAnnotation.objects.filter(final=True).count() == 2
    assert Feature.objects.annotation_needed().count() == 1
