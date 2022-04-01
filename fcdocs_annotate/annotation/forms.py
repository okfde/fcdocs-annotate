from annotation.models import Feature
from django import forms


class FeatureForm(forms.Form):
    document = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for feature in Feature.objects.all():
            key = "feature_{}".format(str(feature.id))
            label = feature.question
            help = feature.description
            options = (('true', 'Ja'), ('false', 'Nein'))
            self.fields[key] = forms.ChoiceField(
                choices=options,
                widget=forms.RadioSelect(attrs={'class': "list-unstyled"}),
                required=True,
                label=label,
                help_text=help
            )
