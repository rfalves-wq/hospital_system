from django import forms
from .models import ClassificacaoRisco


class ClassificacaoForm(forms.ModelForm):

    class Meta:
        model = ClassificacaoRisco
        fields = "__all__"

    def save(self, commit=True):
        return super().save(commit=commit)