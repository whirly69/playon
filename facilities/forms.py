from django import forms
from .models import Structure

class StructureForm(forms.ModelForm):
    class Meta:
        model = Structure
        fields = ['name', 'address', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }