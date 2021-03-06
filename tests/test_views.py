import pytest
from fcdocs_annotate.annotation.models import (
    Feature,
    FeatureAnnotation,
    FeatureAnnotationDraft,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "document_count, answered_documents",
    [
        (3, 0),
        (100, 0),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (100, 1),
        (3, 3),
        (100, 100),
    ],
)
def test_annotate_view_get(
    client,
    get_documents,
    get_features,
    document_count,
    get_annotation_drafts,
    answered_documents,
):

    session = client.session
    features = get_features(2)
    documents = get_documents(document_count)
    get_annotation_drafts(answered_documents, documents, features, session)
    annotated_documents = FeatureAnnotationDraft.objects.users_documents(
        session
    ).values_list("id", flat=True)

    assert len(annotated_documents) == answered_documents
    documents_without_annotation = [
        d for d in documents if d.id not in annotated_documents
    ]

    response = client.get("/annotate/")
    if documents_without_annotation:
        assert response.context_data.get("object") in documents_without_annotation
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
    assert response.context_data.get("object") in [d1, d2, d3]
    for entry in response.context_data.get("feature_form_set").initial:
        assert entry.get("document") in [d1.id, d2.id, d3.id]
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
    assert not response.context_data.get("feature_form_set")

    assert FeatureAnnotationDraft.objects.all().count() == 6
    assert FeatureAnnotation.objects.all().count() == 0
    assert Feature.objects.annotation_needed().count() == 2


@pytest.mark.django_db
def test_annotate_view_clear_session_after_feature_added(
    get_documents, get_features, get_annotation_drafts, client
):
    documents = get_documents(3)
    features = get_features(1)
    session = client.session
    session.save()

    get_annotation_drafts(2, documents, features, session)

    assert Feature.objects.documents_for_annotation(session).count() == 1

    response = client.get("/annotate/")
    assert response.context_data.get("object") == documents[-1]
    assert len(response.context_data.get("feature_form_set").initial) == 1

    get_features(1)

    response = client.get("/annotate/")
    assert response.context_data.get("object") in documents
    formset = response.context_data.get("feature_form_set")
    assert len(formset.initial) == 1


@pytest.mark.django_db
def test_skipped(
    client, get_documents, feature_factory, feature_annotation_draft_factory
):

    documents = get_documents(5)
    feature = feature_factory()

    session_1 = "abc"

    feature_annotation_draft_factory(
        document=documents[0], feature=feature, session=session_1
    )
    feature_annotation_draft_factory(
        document=documents[1], feature=feature, session=session_1
    )

    response = client.get("/annotate/")
    assert response.context_data.get("object") in [documents[0], documents[1]]
    formset = response.context_data.get("feature_form_set")
    assert len(formset.initial) == 1

    session = client.session
    session["skipped_documents"] = [documents[0].id, documents[1].id]
    session.save()

    response = client.get("/annotate/")
    assert response.context_data.get("object") in [
        documents[2],
        documents[3],
        documents[4],
    ]
    formset = response.context_data.get("feature_form_set")
    assert len(formset.initial) == 1
