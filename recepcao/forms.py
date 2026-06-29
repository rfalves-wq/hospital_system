from django import forms
from .models import Recepcao


class RecepcaoForm(forms.ModelForm):

    class Meta:

        model = Recepcao

        fields = "__all__"
    
    def save(self, commit=True):
        return super().save(commit=commit)
    
    email = forms.EmailField(
    required=False,
    widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "exemplo@email.com",
    })
)