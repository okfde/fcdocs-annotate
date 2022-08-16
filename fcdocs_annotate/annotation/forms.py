from django import forms
from django.forms import formset_factory

from filingcabinet import get_document_model

from .models import Feature, FeatureAnnotationDraft

Document = get_document_model()


class SkipDocumentForm(forms.Form):
    document = forms.CharField(widget=forms.HiddenInput())


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
        feature_id = self.initial.get("feature")
        if feature_id:
            try:
                return Feature.objects.get(id=feature_id).question
            except Feature.DoesNotExist:
                return ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["value"] = forms.BooleanField(label=self.get_label())
        self.fields["value"].required = False

    def clean_value(self):
        value = self.cleaned_data.get("value")
        if value == "":
            return False
        return value


class PredictFeatureForm(forms.Form):
    feature = forms.ModelChoiceField(queryset=Feature.objects.exclude(model_path=""))


feature_annotation_draft_formset = formset_factory(FeatureAnnotationDraftForm, extra=0)
