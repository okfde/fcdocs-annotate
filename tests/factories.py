import factory
from filingcabinet import get_document_model

from fcdocs_annotate.annotation.models import (
    TYPE_MANUAL,
    Feature,
    FeatureAnnotation,
    FeatureAnnotationDraft,
)

Document = get_document_model()


class FeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feature

    name = factory.Faker("text")
    question = factory.Faker("text")


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document


class FeatureAnnotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeatureAnnotation

    document = factory.SubFactory(DocumentFactory)
    feature = factory.SubFactory(FeatureFactory)
    type = TYPE_MANUAL


class FeatureAnnotationDraftFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeatureAnnotationDraft

    document = factory.SubFactory(DocumentFactory)
    feature = factory.SubFactory(FeatureFactory)
    session = factory.Faker("random_digit")
