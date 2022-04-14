import pytest
from annotation.models import TYPE_AUTOMATED, TYPE_MANUAL, Feature, FeatureAnnotation
from filingcabinet import get_document_model

Document = get_document_model()


@pytest.mark.django_db
def test_feature_manager(get_features, get_documents, feature_annotation_factory):

    d1, d2, d3, d4 = get_documents(4)
    f1, f2, f3 = get_features(3, documents_needed=3)

    assert Document.objects.all().count() == 4
    assert Feature.objects.all().count() == 3

    fa1 = feature_annotation_factory(
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL, session="a"
    )
    feature_annotation_factory(
        document=d1,
        feature=f1,
        value=True,
        final=True,
        type=TYPE_MANUAL,
        session="b",
    )
    feature_annotation_factory(
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL, session="c"
    )
    feature_annotation_factory(
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL, session="d"
    )
    feature_annotation_factory(
        document=d2, feature=f2, final=False, type=TYPE_MANUAL, session="e"
    )
    feature_annotation_factory(
        document=d3, feature=f3, final=False, type=TYPE_AUTOMATED, session="f"
    )
    feature_annotation_factory(
        document=d4, feature=f1, final=True, value=True, type=TYPE_MANUAL, session="g"
    )
    feature_annotation_factory(
        document=d4, feature=f1, final=True, value=True, type=TYPE_MANUAL, session="h"
    )

    assert fa1.feature == f1
    assert fa1.id in f1.feature_annotations.all().values_list("id", flat=True)

    assert FeatureAnnotation.objects.all().count() == 8
    assert FeatureAnnotation.objects.filter(final=True, type=TYPE_MANUAL).first() == fa1
    assert f1.final_annotation_count() == 6
    assert (
        Feature.objects.with_final_annotations_count()
        .filter(final_annotations_count=6)
        .first()
        == f1
    )
    assert f1 not in Feature.objects.annotation_needed()
    assert f2 in Feature.objects.annotation_needed()


@pytest.mark.django_db
def test_feature_annotation_logic(
    feature_factory, document_factory, feature_annotation_factory
):

    f1 = feature_factory()
    d1 = document_factory()

    feature_annotation_factory(
        feature=f1, document=d1, value=True, final=False, type=TYPE_MANUAL
    )

    assert FeatureAnnotation.objects.all().count() == 1
    assert FeatureAnnotation.objects.filter(final=True).count() == 0

    feature_annotation_factory(
        feature=f1, document=d1, value=True, final=False, type=TYPE_MANUAL
    )

    assert FeatureAnnotation.objects.all().count() == 1
    assert FeatureAnnotation.objects.filter(final=True).count() == 1

    f2 = feature_factory()
    d2 = document_factory()

    feature_annotation_factory(
        feature=f2, document=d2, value=True, final=False, type=TYPE_MANUAL
    )
    feature_annotation_factory(
        feature=f2, document=d2, value=False, final=False, type=TYPE_MANUAL
    )
    assert FeatureAnnotation.objects.filter(feature=f2, document=d2).count() == 2

    feature_annotation_factory(
        feature=f2, document=d2, value=True, final=False, type=TYPE_MANUAL
    )
    assert FeatureAnnotation.objects.filter(feature=f2, document=d2).count() == 1


@pytest.mark.django_db
def test_documents_for_annotation(
    get_documents, feature_factory, feature_annotation_factory
):
    documents = get_documents(1000)
    d1 = documents[340]
    d2 = documents[730]

    user_1_session = "abc"
    user_2_session = "def"
    feature = feature_factory()

    # Annotations for user 1
    feature_annotation_factory(
        document=d1, feature=feature, value=True, session=user_1_session
    )
    feature_annotation_factory(
        document=d2, feature=feature, value=True, session=user_1_session
    )

    # no final annotations exist
    assert FeatureAnnotation.objects.filter(final=True).count() == 0

    # list of documents is sorted with annotated documents first
    documents_for_annotation = Feature.objects.documents_for_annotation()
    assert documents_for_annotation.first() == d1
    assert documents_for_annotation[1] == d2
    assert documents_for_annotation.count() == 1000

    # Annotations for user 2
    feature_annotation_factory(
        document=d1, feature=feature, session=user_2_session, value=True
    )
    feature_annotation_factory(
        document=d2, feature=feature, session=user_2_session, value=True
    )

    # as user 2 did same annotation as user 1 final annotations exist now
    assert FeatureAnnotation.objects.filter(final=True).count() == 2
    assert FeatureAnnotation.objects.filter(final=True).first().document == d1
    assert FeatureAnnotation.objects.filter(final=True).last().document == d2

    # list of documents is sorted with annotated documents first, documents with final annotation excluded
    documents_for_annotation = Feature.objects.documents_for_annotation()
    assert documents_for_annotation.first() == documents[0]
    assert documents_for_annotation[1] == documents[1]
    assert documents_for_annotation.count() == 998

    documents_for_annotation = Feature.objects.documents_for_annotation()
    users_documents = Feature.objects.documents_done_by_user(
        session=user_1_session
    ).values_list("id", flat=True)

    assert list(users_documents) == []
    documents_for_user = documents_for_annotation.exclude(id__in=users_documents)
    assert documents_for_user.count() == 998
    assert documents_for_user.first() == documents[0]
    assert d1.id not in list(documents_for_user.values_list("id", flat=True))
    assert d2.id not in list(documents_for_user.values_list("id", flat=True))

    documents_for_annotation = Feature.objects.documents_for_annotation()
    users_documents = Feature.objects.documents_done_by_user(
        session=user_2_session
    ).values_list("id", flat=True)

    assert d1.id in users_documents
    documents_for_user = documents_for_annotation.exclude(id__in=users_documents)
    assert documents_for_user.count() == 998
    assert d1.id not in list(documents_for_user.values_list("id", flat=True))
    assert d2.id not in list(documents_for_user.values_list("id", flat=True))
