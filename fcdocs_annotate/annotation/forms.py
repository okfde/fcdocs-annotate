from django import forms
from django.forms import formset_factory

from filingcabinet import get_document_model

from .models import Feature, FeatureAnnotationDraft

Document = get_document_model()


class FeatureAnnotationDraftForm(forms.ModelForm):
    document = forms.ModelChoiceField(
        queryset=Document.objects.all(), widget=forms.HiddenInput()
    )
    feature = forms.ModelChoiceField(
        queryset=Feature.objects.all(), widget=forms.HiddenInput()
    )

    class Meta:
        model = FeatureAnnotationDraft
        fields = ["value", "document", "feature"]

    def get_label(self):
        if self.initial.get("feature"):
            try:
                feature_id = self.initial.get("feature")
                return Feature.objects.get(id=feature_id).question
            except Feature.DoesNotExist:
                return ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = ((True, "Ja"), (False, "Nein"))
        self.fields["value"] = forms.ChoiceField(
            choices=options,
            widget=forms.RadioSelect(attrs={"class": "list-unstyled"}),
            label=self.get_label(),
        )


feature_annotation_draft_formset = formset_factory(FeatureAnnotationDraftForm, extra=0)
