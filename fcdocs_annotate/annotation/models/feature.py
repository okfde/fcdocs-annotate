from django.db import models
from django.db.models import Count, Exists, F, Max, OuterRef, Q
from filingcabinet import get_document_model

from .feature_annotation import TYPE_MANUAL, FeatureAnnotation
from .feature_annotation_draft import FeatureAnnotationDraft

Document = get_document_model()


class FeatureManager(models.Manager):
    def _get_session_key(self, session):
        if hasattr(session, "session_key"):
            session = session.session_key
        return session

    def with_final_annotations_count(self):
        return self.annotate(
            final_annotations_count=Count(
                "fcdocs_annotation_featureannotation_annotations",
                filter=(
                    Q(fcdocs_annotation_featureannotation_annotations__value=True)
                    & Q(
                        fcdocs_annotation_featureannotation_annotations__type=TYPE_MANUAL
                    )
                ),
            )
        )

    def with_document_session_annotation(self, document, session):
        subquery_session = FeatureAnnotationDraft.objects.filter(
            document=document, session=session, feature=OuterRef("id")
        )
        return self.annotation_needed().annotate(
            document_session_annotation_exists=Exists(subquery_session)
        )

    def max_annotations_needed(self):
        return (
            self.all().aggregate(Max("documents_needed")).get("documents_needed__max")
        )

    def annotation_needed(self):
        return self.with_final_annotations_count().filter(
            final_annotations_count__lt=F("documents_needed")
        )

    def unfinished_documents_for_user(self, session):
        session = self._get_session_key(session)
        finished_ids = FeatureAnnotation.objects.final_documents().values_list(
            "id", flat=True
        )
        not_done_by_user = FeatureAnnotationDraft.objects.documents_not_done_by_user(
            session
        )
        return not_done_by_user.exclude(id__in=finished_ids)

    def documents_for_annotation(self, session):
        if self.annotation_needed():
            documents = self.unfinished_documents_for_user(session)
            if not documents:
                user_documents = FeatureAnnotationDraft.objects.users_documents(session)
                feature_max = self.max_annotations_needed()
                if user_documents.count() >= feature_max:
                    return Document.objects.none()
                else:
                    annotated_documents_ids = (
                        FeatureAnnotation.objects.documents_with_annotations_ids()
                    )
                    user_documents_ids = user_documents.values_list("id", flat=True)
                    document_ids = list(annotated_documents_ids) + list(
                        user_documents_ids
                    )
                    return Document.objects.all().exclude(id__in=document_ids)
            return documents
        return Document.objects.none()


class Feature(models.Model):
    name = models.CharField(max_length=500)
    question = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    documents_needed = models.PositiveIntegerField(default=10)

    objects = FeatureManager()

    def __str__(self):
        return self.name

    def _get_session_key(self, session):
        if hasattr(session, "session_key"):
            session = session.session_key
        return session

    @property
    def feature_annotations(self):
        return self.fcdocs_annotation_featureannotation_annotations

    @property
    def feature_annotation_drafts(self):
        return self.fcdocs_annotation_featureannotationdraft_annotations

    def final_annotation_count(self):
        annotations = self.feature_annotations.filter(value=True, type=TYPE_MANUAL)
        return annotations.count()

    def needs_annotation(self, session, document):
        session = self._get_session_key(session)
        document_has_final_annotation = self.feature_annotations.filter(
            document=document
        )
        document_has_annotation_from_user = self.feature_annotation_drafts.filter(
            document=document, session=session
        )
        return (
            not document_has_final_annotation and not document_has_annotation_from_user
        )
