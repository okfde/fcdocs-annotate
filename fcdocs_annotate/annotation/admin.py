from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.sites import AlreadyRegistered
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from filingcabinet import get_document_model
from filingcabinet.admin import (
    DocumentBaseAdmin,
    DocumentPortalAdmin,
    PageAdmin,
    PageAnnotationAdmin,
)
from filingcabinet.models import DocumentPortal, Page, PageAnnotation

from .forms import PredictFeatureForm
from .models import TYPE_MANUAL, Feature, FeatureAnnotation, FeatureAnnotationDraft
from .tasks import predict_feature_for_documents

Document = get_document_model()


class FeatureAnnotationAdmin(admin.ModelAdmin):
    model = FeatureAnnotation
    list_display = (
        "get_document_title",
        "value",
        "feature",
    )
    list_filter = ("feature", "type")
    raw_id_fields = ("document",)
    ordering = ("-document",)

    def get_document_title(self, obj):
        SHORTEN = 30
        title = "{} {}".format(str(obj.document.id), obj.document.title)
        if len(title) > SHORTEN:
            return title[:SHORTEN] + ".."
        return title


class FeatureAnnotationDraftAdmin(admin.ModelAdmin):
    model = FeatureAnnotationDraft
    list_display = (
        "session",
        "document_id",
        "value",
        "feature",
    )
    raw_id_fields = ("document",)

    actions = ["make_finalized"]

    @admin.action(description="Finalize selected drafts")
    def make_finalized(modeladmin, request, queryset):
        for draft in queryset:
            FeatureAnnotation.objects.get_or_create(
                defaults={"value": draft.value},
                document=draft.document,
                feature=draft.feature,
                type=TYPE_MANUAL,
            )


class FeatureAdmin(admin.ModelAdmin):
    model = Feature
    list_display = ("name", "documents_needed", "get_document_count")

    def get_document_count(self, obj):
        return obj.final_annotation_count()

    get_document_count.short_description = "Number of documents with that feature"


class ProxyDocument(Document):
    class Meta:
        proxy = True
        verbose_name = "Document with Prediction"
        verbose_name_plural = "Documents with Predictions"


class PredictFeatureAdmin(admin.ModelAdmin):
    model = ProxyDocument
    actions = ["predict_feature"]

    def predict_feature(self, request, queryset):
        if request.POST.get("post"):
            feature_id = request.POST.get("feature")
            documents_list = [
                int(doc) for doc in request.POST.getlist("_selected_action")
            ]
            predict_feature_for_documents.delay(feature_id, documents_list)
            self.message_user(
                request,
                "Started annotating documents. This might take while. Check this page again later.",
            )
            return HttpResponseRedirect(
                reverse("admin:fcdocs_annotation_featureannotation_changelist")
            )

        form = PredictFeatureForm()
        return render(
            request,
            "admin/predict_feature.html",
            context={
                "documents": queryset,
                "form": form,
                "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            },
        )

    predict_feature.short_description = "Predict feature"


admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureAnnotationDraft, FeatureAnnotationDraftAdmin)
admin.site.register(FeatureAnnotation, FeatureAnnotationAdmin)
admin.site.register(ProxyDocument, PredictFeatureAdmin)

try:
    admin.site.register(Page, PageAdmin)
    admin.site.register(PageAnnotation, PageAnnotationAdmin)
    admin.site.register(Document, DocumentBaseAdmin)
    admin.site.register(DocumentPortal, DocumentPortalAdmin)
except AlreadyRegistered:
    pass
