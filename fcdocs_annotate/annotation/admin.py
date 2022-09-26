from django.contrib import admin
from django.contrib.admin import helpers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import PredictFeatureForm
from .models import TYPE_MANUAL, Feature, FeatureAnnotation, FeatureAnnotationDraft
from .tasks import predict_feature_for_documents


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


def predict_feature(self, request, queryset):
    if request.POST.get("post"):
        feature_id = request.POST.get("feature")
        documents_list = [int(doc) for doc in request.POST.getlist("_selected_action")]
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
