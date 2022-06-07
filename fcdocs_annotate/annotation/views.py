import random

from django.contrib.sessions.models import Session
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.views.generic import DetailView, TemplateView

from fcdocs_annotate.annotation.models.feature_annotation_draft import (
    FeatureAnnotationDraft,
)
from filingcabinet import get_document_model
from filingcabinet.views import get_document_viewer_context, get_viewer_preferences

from .forms import SkipDocumentForm, feature_annotation_draft_formset
from .models import Feature

Document = get_document_model()


class AnnotationsOverviewView(TemplateView):
    template_name = "fcdocs_annotation/annotations_overview.html"


class AnnotateDocumentView(DetailView):
    model = Document
    template_name = "fcdocs_annotation/annotate_document.html"

    @cached_property
    def object(self):
        return self.get_object()

    @cached_property
    def documents(self):
        return self.get_queryset()

    def get_queryset(self):
        skipped_documents = self.request.session.get("skipped_documents", [])
        return Feature.objects.documents_for_annotation(self.request.session).exclude(
            id__in=skipped_documents
        )

    def get_object(self, queryset=None):
        document_count = self.documents.count()
        if document_count > 1000:
            max_id = self.documents.aggregate(max_id=Max("id"))["max_id"]
            random_ids = random.sample(range(1, max_id), 100)
            document = self.documents.filter(id__in=random_ids).first()
            if document:
                return document
            return self.documents.first()
        return self.documents.order_by("?").first()

    def get_initial_data(self):
        initial = []
        features = Feature.objects.annotation_needed()
        for feature in features:
            if feature.needs_annotation(self.request.session, self.object):
                initial.append({"document": self.object.id, "feature": feature.id})
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.object:
            ctx.update(
                get_document_viewer_context(
                    self.object,
                    self.request,
                    defaults=get_viewer_preferences(self.request.GET),
                )
            )
            ctx.update(
                {
                    "feature_form_set": feature_annotation_draft_formset(
                        initial=self.get_initial_data()
                    ),
                    "skipform": SkipDocumentForm(
                        initial={"document": str(self.object.id)}
                    ),
                }
            )
        return ctx

    def post(self, request, *args, **kwargs):
        if "skip" in request.POST:
            skipform = SkipDocumentForm(request.POST)
            if skipform.is_valid():
                document = skipform.cleaned_data.get("document")
                skipped_documents = request.session.get("skipped_documents", [])
                skipped_documents.append(int(document))
                request.session["skipped_documents"] = skipped_documents
        else:
            form_set = feature_annotation_draft_formset(request.POST)
            if form_set.is_valid():
                if not self.request.session.session_key:
                    self.request.session.create()
                session = Session.objects.get(
                    session_key=self.request.session.session_key
                )
                for form in form_set:
                    if form.is_valid():
                        annotation = form.save(commit=False)
                        annotation.session = session
                        try:
                            annotation.save()
                        except FeatureAnnotationDraft.IntegrityError:
                            pass
        return HttpResponseRedirect(self.request.path_info)
