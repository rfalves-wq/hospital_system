from django import forms

from medico.models import ConsultaMedica


class ResultadoImagemForm(forms.ModelForm):

    class Meta:
        model = ConsultaMedica

        fields = [
            "resultado_exames_imagem",
        ]

        widgets = {
            "resultado_exames_imagem": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Digite aqui o resultado / laudo do exame de imagem..."
            }),
        }