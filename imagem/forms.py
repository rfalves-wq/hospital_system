from django import forms

from medico.models import ConsultaMedica


class ResultadoImagemForm(forms.ModelForm):

    CAMPOS_POR_SETOR = {
        "raiox": [
            "resultado_raiox",
            "tecnico_raiox_nome",
            "tecnico_raiox_registro",
        ],
        "tomografia": [
            "resultado_tomografia",
            "tecnico_tomografia_nome",
            "tecnico_tomografia_registro",
        ],
        "mamografia": [
            "resultado_mamografia",
            "tecnico_mamografia_nome",
            "tecnico_mamografia_registro",
        ],
        "densitometria": [
            "resultado_densitometria",
            "tecnico_densitometria_nome",
            "tecnico_densitometria_registro",
        ],
    }

    class Meta:
        model = ConsultaMedica

        fields = [
            "resultado_raiox",
            "tecnico_raiox_nome",
            "tecnico_raiox_registro",

            "resultado_tomografia",
            "tecnico_tomografia_nome",
            "tecnico_tomografia_registro",

            "resultado_mamografia",
            "tecnico_mamografia_nome",
            "tecnico_mamografia_registro",

            "resultado_densitometria",
            "tecnico_densitometria_nome",
            "tecnico_densitometria_registro",
        ]

        widgets = {
            "resultado_raiox": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Digite o resultado/laudo do Raio-X",
            }),
            "tecnico_raiox_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do técnico do Raio-X",
            }),
            "tecnico_raiox_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro do técnico do Raio-X",
            }),

            "resultado_tomografia": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Digite o resultado/laudo da Tomografia",
            }),
            "tecnico_tomografia_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do técnico da Tomografia",
            }),
            "tecnico_tomografia_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro do técnico da Tomografia",
            }),

            "resultado_mamografia": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Digite o resultado/laudo da Mamografia",
            }),
            "tecnico_mamografia_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do técnico da Mamografia",
            }),
            "tecnico_mamografia_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro do técnico da Mamografia",
            }),

            "resultado_densitometria": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Digite o resultado/laudo da Densitometria",
            }),
            "tecnico_densitometria_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do técnico da Densitometria",
            }),
            "tecnico_densitometria_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro do técnico da Densitometria",
            }),
        }

    def __init__(self, *args, **kwargs):
        setor = kwargs.pop("setor", None)

        super().__init__(*args, **kwargs)

        if setor in self.CAMPOS_POR_SETOR:
            campos_permitidos = self.CAMPOS_POR_SETOR[setor]

            for campo in list(self.fields.keys()):
                if campo not in campos_permitidos:
                    self.fields.pop(campo)