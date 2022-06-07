from django.conf import settings

import pytest
from fcdocs_annotate.annotation.models import (
    Feature,
    FeatureAnnotation,
    FeatureAnnotationDraft,
)
from filingcabinet import get_document_model

Document = get_document_model()


@pytest.mark.django_db
def test_documents_manager_documents_with_and_without_annotations(
    get_features, get_documents, get_annotation_drafts, get_annotations
):

    documents = get_documents(1000)
    features = get_features(10)
    session = "abc"
    get_annotation_drafts(5, documents, features, session)
    get_annotations(7, documents, features)
    assert (
        FeatureAnnotationDraft.objects.documents_with_annotation_drafts().count() == 5
    )
    assert (
        FeatureAnnotationDraft.objects.documents_without_annotation_drafts().count()
        == 995
    )
    assert FeatureAnnotation.objects.documents_with_annotations().count() == 7
    assert FeatureAnnotation.objects.documents_without_annotations().count() == 993


@pytest.mark.django_db
def test_documents_manager_final_documents(
    get_features, get_documents, get_annotations
):

    documents = get_documents(1000)
    features = get_features(2)
    get_annotations(5, documents, features)

    assert FeatureAnnotation.objects.final_documents().count() == 5


@pytest.mark.django_db
def test_documents_manager_users_documents(
    get_features, get_documents, get_annotation_drafts
):

    documents = get_documents(1000)
    features = get_features(2)
    session = "abc"
    get_annotation_drafts(5, documents, features, session)

    d1 = documents[0]
    d2 = documents[1]

    FeatureAnnotationDraft.objects.filter(document_id__in=[d1.id, d2.id]).update(
        session="def"
    )
    assert FeatureAnnotationDraft.objects.users_documents("def").count() == 2


@pytest.mark.django_db
def test_annotations_final_annotations(
    get_documents, feature_factory, feature_annotation_factory
):
    documents = get_documents(5)

    assert Document.objects.all().count() == 5

    f1 = feature_factory(documents_needed=1)
    f2 = feature_factory(documents_needed=1)
    f3 = feature_factory(documents_needed=10)
    f4 = feature_factory(documents_needed=10)

    assert Feature.objects.annotation_needed().count() == 4

    feature_annotation_factory(document=documents[0], feature=f1, value=True)
    feature_annotation_factory(document=documents[0], feature=f2, value=True)

    assert Feature.objects.annotation_needed().count() == 2
    assert FeatureAnnotation.objects.final_documents().count() == 0

    feature_annotation_factory(document=documents[0], feature=f3, value=True)
    feature_annotation_factory(document=documents[0], feature=f4, value=True)

    assert Feature.objects.annotation_needed().count() == 2
    assert FeatureAnnotation.objects.final_documents().count() == 1

    f3.documents_needed = 1
    f3.save()

    assert Feature.objects.annotation_needed().count() == 1
    assert FeatureAnnotation.objects.final_documents().count() == 1


@pytest.mark.django_db
def test_annotations_draft_not_done_by_user(
    get_documents,
    feature_factory,
    feature_annotation_factory,
    feature_annotation_draft_factory,
):
    documents = get_documents(5)

    assert Document.objects.all().count() == 5

    f1 = feature_factory(documents_needed=1)
    f2 = feature_factory(documents_needed=1)
    f3 = feature_factory(documents_needed=10)
    f4 = feature_factory(documents_needed=10)

    feature_annotation_factory(document=documents[0], feature=f1, value=True)
    feature_annotation_factory(document=documents[0], feature=f2, value=True)

    assert Feature.objects.annotation_needed().count() == 2

    session1 = "abc"
    session2 = "def"

    feature_annotation_draft_factory(
        document=documents[0], feature=f3, session=session1, value=True
    )
    feature_annotation_draft_factory(
        document=documents[0], feature=f4, session=session1, value=True
    )

    assert (
        FeatureAnnotationDraft.objects.documents_not_done_by_user(session2).count() == 1
    )

    feature_annotation_draft_factory(
        document=documents[0], feature=f1, session=session2, value=True
    )
    feature_annotation_draft_factory(
        document=documents[0], feature=f2, session=session2, value=True
    )

    assert (
        FeatureAnnotationDraft.objects.documents_not_done_by_user(session2).count() == 1
    )
    assert (
        Feature.objects.unfinished_documents_for_user(session2).first() == documents[0]
    )
    assert Feature.objects.unfinished_documents_for_user(session2).count() == 1


@pytest.mark.django_db
def test_documents_manager_unfinished_documents(
    get_features, get_documents, feature_annotation_factory
):

    documents = get_documents(1000)
    features = get_features(2)
    feature_annotation_factory(document=documents[0], feature=features[0])

    assert FeatureAnnotation.objects.unfinished_documents().count() == 1


@pytest.mark.django_db
def test_documents_manager_documents_not_done_by_user(
    get_features, get_documents, get_annotation_drafts
):

    documents = get_documents(1000)
    features = get_features(2)
    session = "abc"
    get_annotation_drafts(5, documents, features, session)

    d1 = documents[0]
    d2 = documents[1]

    FeatureAnnotationDraft.objects.filter(document_id__in=[d1.id, d2.id]).update(
        session="def"
    )
    assert FeatureAnnotationDraft.objects.documents_not_done_by_user("def").count() == 3


@pytest.mark.django_db
def test_feature_manager(get_features, get_documents, feature_annotation_factory):

    d1, d2, d3, d4 = get_documents(4)
    f1, f2, f3 = get_features(3, documents_needed=3)

    assert Document.objects.all().count() == 4
    assert Feature.objects.all().count() == 3

    fa1 = feature_annotation_factory(document=d1, feature=f1, value=True)
    feature_annotation_factory(document=d2, feature=f2)
    feature_annotation_factory(document=d3, feature=f3)
    feature_annotation_factory(document=d4, feature=f1, value=True)

    assert fa1.feature == f1
    assert fa1.id in f1.feature_annotations.all().values_list("id", flat=True)

    assert FeatureAnnotation.objects.all().count() == 4
    assert f1.final_annotation_count() == 2
    assert (
        Feature.objects.with_final_annotations_count()
        .filter(final_annotations_count=2)
        .first()
        == f1
    )
    assert f1 in Feature.objects.annotation_needed()
    assert f2 in Feature.objects.annotation_needed()


@pytest.mark.django_db
def test_feature_annotation_logic(
    feature_factory, document_factory, feature_annotation_draft_factory
):

    f1 = feature_factory()
    d1 = document_factory()

    feature_annotation_draft_factory(feature=f1, document=d1, value=True, session="abc")

    assert FeatureAnnotationDraft.objects.all().count() == 1
    assert FeatureAnnotation.objects.all().count() == 0

    feature_annotation_draft_factory(feature=f1, document=d1, value=True, session="def")

    assert FeatureAnnotationDraft.objects.all().count() == 2
    assert FeatureAnnotation.objects.all().count() == 1

    f2 = feature_factory()
    d2 = document_factory()

    feature_annotation_draft_factory(feature=f2, document=d2, value=True, session="abc")
    feature_annotation_draft_factory(
        feature=f2, document=d2, value=False, session="def"
    )
    assert FeatureAnnotationDraft.objects.filter(feature=f2, document=d2).count() == 2

    feature_annotation_draft_factory(feature=f2, document=d2, value=True, session="ghi")
    assert FeatureAnnotationDraft.objects.filter(feature=f2, document=d2).count() == 3
    assert FeatureAnnotation.objects.all().count() == 2


@pytest.mark.django_db
def test_documents_for_annotation(
    get_documents, feature_factory, feature_annotation_draft_factory
):
    documents = get_documents(1000)
    d1 = documents[340]
    d2 = documents[730]

    user_1_session = "abc"
    user_2_session = "def"
    feature = feature_factory()

    # Annotation drafts for user 1
    feature_annotation_draft_factory(
        document=d1, feature=feature, value=True, session=user_1_session
    )
    feature_annotation_draft_factory(
        document=d2, feature=feature, value=True, session=user_1_session
    )

    # no annotations exist
    assert FeatureAnnotation.objects.all().count() == 0
    assert FeatureAnnotation.objects.unfinished_documents().count() == 0

    # list of documents is sorted with annotated documents first
    documents_user_2 = Feature.objects.documents_for_annotation(user_2_session)
    assert documents_user_2.first() == d1
    assert documents_user_2[1] == d2
    assert documents_user_2.count() == 2

    # Annotation drafts for user 2
    feature_annotation_draft_factory(
        document=d1, feature=feature, session=user_2_session, value=True
    )
    feature_annotation_draft_factory(
        document=d2, feature=feature, session=user_2_session, value=True
    )

    # as user 2 did same annotation as user 1 final annotations exist now
    assert FeatureAnnotation.objects.all().count() == 2
    assert FeatureAnnotation.objects.all().first().document == d1
    assert FeatureAnnotation.objects.all().last().document == d2

    # no unfinished documents exists
    assert FeatureAnnotation.objects.unfinished_documents().count() == 0

    # list of documents with final annotation excluded
    documents_for_annotation = Feature.objects.documents_for_annotation(user_2_session)
    assert documents_for_annotation.first() == documents[0]
    assert documents_for_annotation[1] == documents[1]
    assert documents_for_annotation.count() == 998

    # same for user_1
    documents_for_annotation = Feature.objects.documents_for_annotation(user_1_session)
    assert documents_for_annotation.first() == documents[0]
    assert documents_for_annotation[1] == documents[1]
    assert documents_for_annotation.count() == 998

    # add draft for user_1
    feature_annotation_draft_factory(
        document=documents[2], feature=feature, session=user_1_session, value=True
    )

    # user_2 gets documents[2] to annotate
    documents_for_annotation = Feature.objects.documents_for_annotation(user_2_session)
    assert documents_for_annotation.first() == documents[2]

    # user_1 gets documents[0] to annotate
    documents_for_annotation = Feature.objects.documents_for_annotation(user_1_session)
    assert documents_for_annotation.first() == documents[0]

    # user_2 annotates document[2] the same way as user_1
    feature_annotation_draft_factory(
        document=documents[2], feature=feature, session=user_2_session, value=True
    )

    # add another feature
    feature_factory()

    # user_1 gets documents[2] to annotate
    documents_for_annotation = Feature.objects.documents_for_annotation(user_1_session)
    assert documents_for_annotation.first() == documents[2]


@pytest.mark.django_db
def test_publish_signal(document_factory):

    d1 = document_factory(public=False)
    assert d1.public

    settings.FCDOCS_ANNOTATE_PUBLISH_DOCUMENTS = False

    d1 = document_factory(public=False)
    assert not d1.public

    del settings.FCDOCS_ANNOTATE_PUBLISH_DOCUMENTS
    assert not hasattr(settings, "FCDOCS_ANNOTATE_PUBLISH_DOCUMENTS")

    d1 = document_factory(public=False)
    assert not d1.public
