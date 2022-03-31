from django import forms

from annotation.models import Feature


class FeatureForm(forms.Form):
    document = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for feature in Feature.objects.all():
            key = 'feature_{}'.format(str(feature.id))
            label = feature.question
            self.fields[key] = forms.BooleanField(label=label, required=False)
