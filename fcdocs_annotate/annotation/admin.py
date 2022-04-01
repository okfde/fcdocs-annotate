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
        "document",
        "features",
        "final",
    )
    ordering = ("-document",)


admin.site.register(Page, PageAdmin)
admin.site.register(PageAnnotation, PageAnnotationAdmin)
admin.site.register(Document, DocumentBaseAdmin)
admin.site.register(DocumentPortal, DocumentPortalAdmin)
admin.site.register(Feature)
admin.site.register(FeatureAnnotation, FeatureAnnotationAdmin)
