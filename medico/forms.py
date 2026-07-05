from django import forms

from .models import ConsultaMedica


class ConsultaMedicaForm(forms.ModelForm):

    class Meta:
        model = ConsultaMedica

        exclude = [
            "acolhimento",
            "data_consulta",
        ]

        widgets = {
            "medico_responsavel": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do médico responsável",
            }),

            "cid": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CID selecionado",
            }),

            "queixa_principal": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Queixa principal do paciente",
            }),

            "historia_doenca_atual": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "História da doença atual",
            }),

            "exame_fisico": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Achados do exame físico",
            }),

            "hipotese_diagnostica": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Hipótese diagnóstica",
            }),

            "conduta": forms.Select(attrs={
                "class": "form-select",
            }),

            "solicita_medicacao": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "solicita_exames_laboratoriais": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "solicita_exames_imagem": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "exames_laboratoriais": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Ex: Hemograma, glicemia, ureia, creatinina, urina tipo 1, PCR...",
            }),

            "exames_imagem": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Ex: Raio-X, ultrassom, tomografia, ressonância...",
            }),

            "prescricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Prescrição médica",
            }),

            "orientacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Orientações ao paciente",
            }),
        }