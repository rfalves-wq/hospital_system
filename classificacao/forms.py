from django import forms

from .models import ClassificacaoRisco


class ClassificacaoForm(forms.ModelForm):

    class Meta:
        model = ClassificacaoRisco

        exclude = [
            "acolhimento",
            "data_classificacao",
        ]

        widgets = {
            "data_chegada": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),

            "hora_chegada": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
            }),

            "forma_chegada": forms.Select(attrs={
                "class": "form-control",
            }),

            "usuario_responsavel": forms.TextInput(attrs={
                "class": "form-control",
            }),

            "queixa_principal": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),

            "tempo_inicio_sintoma": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 2 horas, 3 dias",
            }),

            "escala_dor": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 10,
            }),

            "doenca_pre_existente": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),

            "alergia": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),

            "uso_medicamento": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),

            "possivel_gravidez": forms.Select(attrs={
                "class": "form-control",
            }),

            "deficiencia": forms.TextInput(attrs={
                "class": "form-control",
            }),

            "cor": forms.RadioSelect(),

            

            "saturacao": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 100,
            }),

            "glicemia": forms.NumberInput(attrs={
                "class": "form-control",
            }),

            "peso": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),

            "altura": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),

            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),
        }