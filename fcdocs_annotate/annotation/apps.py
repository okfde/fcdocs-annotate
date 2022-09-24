from django.apps import AppConfig


class AnnotationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fcdocs_annotate.annotation"
    label = "fcdocs_annotation"

    def ready(self):
        from django.contrib import admin

        import fcdocs_annotate.annotation.signals  # NOQA
        from filingcabinet import get_document_model

        from .admin import predict_feature

        Document = get_document_model()

        admin.site._registry[Document].predict_feature = predict_feature
        admin.site._registry[Document].actions += ["predict_feature"]
