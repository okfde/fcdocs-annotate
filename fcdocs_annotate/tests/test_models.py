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
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL
    )
    feature_annotation_factory(
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL
    )
    feature_annotation_factory(
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL
    )
    feature_annotation_factory(
        document=d1, feature=f1, value=True, final=True, type=TYPE_MANUAL
    )
    feature_annotation_factory(document=d2, feature=f2, final=False, type=TYPE_MANUAL)
    feature_annotation_factory(
        document=d3, feature=f3, final=False, type=TYPE_AUTOMATED
    )
    feature_annotation_factory(
        document=d4, feature=f1, final=True, value=True, type=TYPE_MANUAL
    )
    feature_annotation_factory(
        document=d4, feature=f1, final=True, value=True, type=TYPE_MANUAL
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

    assert Feature.objects.documents_for_annotation().last() == d1
    assert d2 in Feature.objects.documents_for_annotation()


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
