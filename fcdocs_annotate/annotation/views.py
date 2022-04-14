from annotation.forms import feature_annotation_formset
from annotation.models import TYPE_MANUAL, Feature
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.views.generic import DetailView
from filingcabinet import get_document_model
from filingcabinet.views import get_document_viewer_context, get_viewer_preferences

Document = get_document_model()


class AnnotateDocumentView(DetailView):
    model = Document
    template_name = "fcdocs_annotation/annotate_document.html"

    @cached_property
    def object(self):
        return self.get_object()

    def get_queryset(self):
        documents = Feature.objects.documents_for_annotation()
        users_documents = Feature.objects.documents_done_by_user(
            session=self.request.session
        ).values_list("id", flat=True)
        return documents.exclude(id__in=users_documents)

    def get_object(self, queryset=None):
        return self.get_queryset().first()

    def get_initial_data(self):
        initial = []
        document = self.object
        session = self.request.session.session_key
        features = Feature.objects.with_document_session_annotation(
            document, session
        ).filter(document_session_annotation_exists=False)
        for feature in features:
            initial.append({"document": self.object.id, "feature": feature.id})

        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"progress": self.get_progress_for_user()})
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
                    "feature_form_set": feature_annotation_formset(
                        initial=self.get_initial_data()
                    )
                }
            )
        return ctx

    def get_progress_for_user(self):
        annotated_documents = Feature.objects.documents_done_by_user(
            self.request.session
        ).values_list("id", flat=True)
        document_count = Feature.objects.documents_for_annotation().count()
        if not (
            len(annotated_documents) == 0 or document_count == 0
        ) and document_count >= len(annotated_documents):
            return int(len(annotated_documents) * 100 / document_count)
        return 0

    def post(self, request, *args, **kwargs):
        form_set = feature_annotation_formset(request.POST)

        if form_set.is_valid():
            if not self.request.session.session_key:
                self.request.session.create()
            session = Session.objects.get(session_key=self.request.session.session_key)
            for form in form_set:
                if form.is_valid():
                    annotation = form.save(commit=False)
                    annotation.type = TYPE_MANUAL
                    annotation.final = False
                    annotation.session = session
                    annotation.save()
        return HttpResponseRedirect(self.request.path_info)
