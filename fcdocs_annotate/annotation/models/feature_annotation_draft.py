import collections

from django.db import models
from django.db.models.functions import Coalesce
from filingcabinet import get_document_model

from .abstract_annotation import AbstractAnnotation, AbstractAnnotationManager
from .feature_annotation import TYPE_MANUAL, FeatureAnnotation

Document = get_document_model()


class AnnotationDraftDocumentsManager(AbstractAnnotationManager):
    def documents_with_annotation_drafts_ids(self):
        return (
            self.all().select_related("documents").values_list("document_id", flat=True)
        )

    def documents_with_annotation_drafts(self):
        return Document.objects.filter(
            id__in=self.documents_with_annotation_drafts_ids()
        )

    def documents_without_annotation_drafts(self):
        document_ids = self.all().values_list("document_id", flat=True)
        return Document.objects.exclude(id__in=document_ids)

    def documents_with_user_count(self, session):
        session = self._get_session_key(session)
        subquery = self._get_subquery({"session": session})
        return self.documents_with_annotation_drafts().annotate(
            user_count=Coalesce(subquery, 0)
        )

    def users_documents(self, session):
        from .feature import Feature

        session = self._get_session_key(session)
        feature_count = Feature.objects.all().count()
        documents = self.documents_with_user_count(session)
        return documents.filter(user_count__gte=feature_count)

    def documents_not_done_by_user(self, session):
        from .feature import Feature

        session = self._get_session_key(session)
        feature_count = Feature.objects.all().count()
        documents = self.documents_with_user_count(session)
        return documents.exclude(user_count__gte=feature_count)


class FeatureAnnotationDraft(AbstractAnnotation):
    session = models.CharField(max_length=255, blank=True)

    objects = AnnotationDraftDocumentsManager()

    class Meta:
        unique_together = ("session", "feature", "document")

    def save(self, *args, **kwargs):
        final, value = self.check_final()
        super().save(*args, **kwargs)
        if final:
            FeatureAnnotation.objects.create(
                value=value,
                document=self.document,
                feature=self.feature,
                type=TYPE_MANUAL,
            )

    def __str__(self):
        SHORTEN = 30
        title = "{} {}".format(str(self.document.id), self.document.title)
        if len(title) > SHORTEN:
            return title[:SHORTEN] + ".."
        return title

    def get_other_annotation_drafts(self):
        return self.document.featureannotationdraft_set.filter(
            feature=self.feature, document=self.document
        ).exclude(id=self.id)

    def check_final(self):
        annotations = self.get_other_annotation_drafts()
        if annotations.count() == 1:
            final = annotations.first().value == self.value
            return final, self.value
        elif annotations.count() > 1:
            value_list = [a.value for a in annotations] + [self.value]
            c = collections.Counter(value_list)
            value, count = c.most_common()[0]
            return True, value
        return False, self.value
