from annotation.forms import FeatureForm
from annotation.models import TYPE_MANUAL, FeatureAnnotation
from django.db.models import Exists, OuterRef
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
        sudbquery = FeatureAnnotation.objects.filter(
            final=True, type=TYPE_MANUAL, document=OuterRef("id")
        )
        documents = Document.objects.annotate(has_annotation=Exists(sudbquery))
        annotated_documents = self.request.session.get("annotated_documents", [])
        return documents.filter(has_annotation=False).exclude(
            id__in=annotated_documents
        )

    def get_object(self, queryset=None):
        return self.get_queryset().first()

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
                {"feature_form": FeatureForm(initial={"document": str(self.object.id)})}
            )
        return ctx

    def get_progress_for_user(self):
        annotated_documents = self.request.session.get("annotated_documents", [])
        document_count = Document.objects.all().count()
        if not (len(annotated_documents) == 0 or document_count == 0):
            return int(len(annotated_documents) * 100 / document_count)
        return 0

    def post(self, request, *args, **kwargs):
        feature_form = FeatureForm(request.POST)
        if feature_form.is_valid():
            cleaned_data = feature_form.cleaned_data
            document_id = cleaned_data.pop("document")
            document = Document.objects.get(id=document_id)
            FeatureAnnotation.objects.create(
                document=document, features=cleaned_data, type=TYPE_MANUAL
            )
            annotated_documents = request.session.get("annotated_documents", [])
            annotated_documents.append(int(document_id))
            request.session["annotated_documents"] = annotated_documents
            return HttpResponseRedirect(self.request.path_info)
