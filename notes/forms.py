from django import forms
from notes.models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        widgets = {
            'recipient': forms.TextInput(attrs={
                'class': 'input-xxlarge typeahead',
                'data-source': 'customers'}),
            'body': forms.Textarea(attrs={
                'class': 'input-xxlarge template', 'rows': 15})
        }
