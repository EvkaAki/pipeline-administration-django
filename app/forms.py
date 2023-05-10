from django import forms
from .models import RunRequest


class AddRunRequestForm(forms.ModelForm):
    class Meta:
        model = RunRequest
        fields = ["message", "pipeline_id", "dataset_id"]


