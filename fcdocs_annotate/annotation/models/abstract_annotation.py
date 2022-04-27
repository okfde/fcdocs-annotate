from django.db import models
from django.db.models import Count, OuterRef, Subquery
from filingcabinet import get_document_model

Document = get_document_model()


class AbstractAnnotationManager(models.Manager):
    def _get_session_key(self, session):
        if hasattr(session, "session_key"):
            session = session.session_key
        return session

    def _get_subquery(self, filters):
        return Subquery(
            self.filter(**filters, document_id=OuterRef("id"))
            .order_by()
            .values("document")
            .annotate(count=Count("pk"))
            .values("count"),
            output_field=models.IntegerField(),
        )


class AbstractAnnotation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    feature = models.ForeignKey(
        "fcdocs_annotation.Feature",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_annotations",
    )
    value = models.BooleanField(null=True)

    class Meta:
        abstract = True
