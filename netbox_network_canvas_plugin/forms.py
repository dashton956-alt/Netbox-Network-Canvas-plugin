from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .models import NetworkTopologyCanvas


class NetworkCanvasForm(NetBoxModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter canvas description...'}),
        required=False,
        help_text='Optional description for this network canvas'
    )
    
    topology_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': 'Enter topology data in JSON format...'}),
        required=False,
        help_text='JSON data representing the network topology'
    )

    class Meta:
        model = NetworkTopologyCanvas
        fields = ("name", "description", "topology_data", "tags")
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter canvas name...'}),
        }


class NetworkCanvasFilterForm(NetBoxModelFilterSetForm):
    model = NetworkTopologyCanvas
    
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Canvas name...'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Description...'})
    )
