from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.views.generic import DetailView, TemplateView
from filingcabinet import get_document_model
from filingcabinet.views import get_document_viewer_context, get_viewer_preferences

from .forms import feature_annotation_draft_formset
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
        return Feature.objects.documents_for_annotation(self.request.session)

    def get_object(self, queryset=None):
        return self.documents.first()

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
                    )
                }
            )
        return ctx

    def post(self, request, *args, **kwargs):
        form_set = feature_annotation_draft_formset(request.POST)

        if form_set.is_valid():
            if not self.request.session.session_key:
                self.request.session.create()
            session = Session.objects.get(session_key=self.request.session.session_key)
            for form in form_set:
                if form.is_valid():
                    annotation = form.save(commit=False)
                    annotation.session = session
                    annotation.save()
        return HttpResponseRedirect(self.request.path_info)
