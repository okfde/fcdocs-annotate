from django.contrib import admin
from filingcabinet.admin import (
    DocumentBaseAdmin,
    DocumentPortalAdmin,
    PageAdmin,
    PageAnnotationAdmin,
)
from filingcabinet.models import Document, DocumentPortal, Page, PageAnnotation

from .models import Feature, FeatureAnnotation


class FeatureAnnotationAdmin(admin.ModelAdmin):
    model = FeatureAnnotation
    list_display = (
        "get_document_title",
        "features",
        "final",
    )
    ordering = ("-document",)

    def get_document_title(self, obj):
        SHORTEN = 30
        title = obj.document.title
        if len(title) > SHORTEN:
            return title[:SHORTEN] + '..'
        return title


class FeatureAdmin(admin.ModelAdmin):
    model = Feature
    list_display = (
        "name",
        "documents_needed",
        "get_document_count"
    )

    def get_document_count(self, obj):
        dict_key = "features__feature_{}".format(obj.id)
        filters = {'final': True}
        filters[dict_key] = 'true'
        return FeatureAnnotation.objects.filter(**filters).count()

    get_document_count.short_description = "Number of documents with that feature"


admin.site.register(Page, PageAdmin)
admin.site.register(PageAnnotation, PageAnnotationAdmin)
admin.site.register(Document, DocumentBaseAdmin)
admin.site.register(DocumentPortal, DocumentPortalAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureAnnotation, FeatureAnnotationAdmin)
