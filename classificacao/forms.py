from django import forms
from .models import ClassificacaoRisco


class ClassificacaoForm(forms.ModelForm):

    class Meta:

        model = ClassificacaoRisco

        exclude = ["acolhimento", "data_classificacao"]

        widgets = {

            "queixa_principal": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),

            "cor": forms.Select(attrs={
                "class": "form-select",
            }),

            "peso": forms.NumberInput(attrs={
                "class": "form-control",
            }),

            "altura": forms.NumberInput(attrs={
                "class": "form-control",
            }),

            "glicemia": forms.NumberInput(attrs={
                "class": "form-control",
            }),

            "saturacao": forms.NumberInput(attrs={
                "class": "form-control",
            }),

            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),

        }