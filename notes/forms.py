from django import forms
from notes.models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note

    recipient = forms.CharField(widget=forms.TextInput(
        attrs={'class': "input-xxlarge typeahead",
        'data-source': "customers"}), required=False)
    body = forms.CharField(widget=forms.Textarea(attrs={
            'class': 'input-xxlarge', 'rows': 6}))
