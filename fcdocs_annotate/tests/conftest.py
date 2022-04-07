from pytest_factoryboy import register

from .factories import DocumentFactory, FeatureAnnotationFactory, FeatureFactory

register(DocumentFactory)
register(FeatureFactory)
register(FeatureAnnotationFactory)
