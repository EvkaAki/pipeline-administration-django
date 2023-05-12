from django import forms
from .models import RunRequest, DatasetRequest


class AddRunRequestForm(forms.ModelForm):
    class Meta:
        model = RunRequest
        fields = ["message", "pipeline_id", "dataset_id", 'pipeline_version_id', 'pipeline_name', 'pipeline_version_name']

        # def __init__(self, *args, **kwargs):
        #     from django.forms.widgets import HiddenInput
        #     self.fields['pipeline_name'].widget = HiddenInput()


class AddDatasetRequestForm(forms.ModelForm):
    class Meta:
        model = DatasetRequest
        fields = ["message", "dataset_id"]

        # def __init__(self, *args, **kwargs):
        #     from django.forms.widgets import HiddenInput
        #     self.fields['pipeline_name'].widget = HiddenInput()


