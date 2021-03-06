from django.apps import AppConfig


class AnnotationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fcdocs_annotate.annotation"
    label = "fcdocs_annotation"

    def ready(self):
        import fcdocs_annotate.annotation.signals  # NOQA
