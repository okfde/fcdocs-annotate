import pytest
from annotation.models import TYPE_AUTOMATED, TYPE_MANUAL, Feature, FeatureAnnotation
from filingcabinet import get_document_model

Document = get_document_model()


@pytest.mark.django_db
def test_feature_manager(feature_factory, document_factory, feature_annotation_factory):

    d1 = document_factory()
    d2 = document_factory()
    d3 = document_factory()
    d4 = document_factory()

    f1 = feature_factory(documents_needed=3)
    f2 = feature_factory(documents_needed=3)
    f3 = feature_factory(documents_needed=3)

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
