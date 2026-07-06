from django import forms

from medico.models import ConsultaMedica


class ResultadoLaboratorioForm(forms.ModelForm):

    class Meta:
        model = ConsultaMedica

        fields = [
            "resultado_exames_laboratoriais",
            "tecnico_laboratorio_nome",
            "tecnico_laboratorio_registro",
        ]

        widgets = {
            "resultado_exames_laboratoriais": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Digite aqui os resultados dos exames laboratoriais..."
            }),

            "tecnico_laboratorio_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do técnico responsável"
            }),

            "tecnico_laboratorio_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro do técnico"
            }),
        }