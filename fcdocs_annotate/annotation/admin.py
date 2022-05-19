from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from filingcabinet.admin import (
    DocumentBaseAdmin,
    DocumentPortalAdmin,
    PageAdmin,
    PageAnnotationAdmin,
)
from filingcabinet.models import Document, DocumentPortal, Page, PageAnnotation

from .models import TYPE_MANUAL, Feature, FeatureAnnotation, FeatureAnnotationDraft


class FeatureAnnotationAdmin(admin.ModelAdmin):
    model = FeatureAnnotation
    list_display = (
        "get_document_title",
        "value",
        "feature",
    )
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


admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureAnnotationDraft, FeatureAnnotationDraftAdmin)
admin.site.register(FeatureAnnotation, FeatureAnnotationAdmin)

try:
    admin.site.register(Page, PageAdmin)
    admin.site.register(PageAnnotation, PageAnnotationAdmin)
    admin.site.register(Document, DocumentBaseAdmin)
    admin.site.register(DocumentPortal, DocumentPortalAdmin)
except AlreadyRegistered:
    pass
