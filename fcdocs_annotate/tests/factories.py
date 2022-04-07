import factory
from annotation.models import Feature, FeatureAnnotation
from filingcabinet import get_document_model

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
