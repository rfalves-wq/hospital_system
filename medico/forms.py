from django import forms

from .models import ConsultaMedica, ReavaliacaoMedica


class ConsultaMedicaForm(forms.ModelForm):

    class Meta:
        model = ConsultaMedica

        fields = [
            "medico_responsavel",
            "crm_medico",
            "cid",
            "queixa_principal",
            "historia_doenca_atual",
            "exame_fisico",
            "hipotese_diagnostica",
            "conduta",
            "solicita_medicacao",
            "solicita_exames_laboratoriais",
            "solicita_exames_imagem",
            "exames_laboratoriais",
            "exames_imagem",
            "indicacao_raiox",
            "indicacao_tomografia",
            "indicacao_outros_imagem",
            "prescricao",
            "orientacoes",
            "receita",
            "atestado",
            "atestado_dias",
            "atestado_cid",
        ]

        widgets = {
            "medico_responsavel": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do médico responsável",
            }),

            "crm_medico": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CRM do médico",
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
                "placeholder": "Exames laboratoriais solicitados",
            }),

            "exames_imagem": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Exames de imagem solicitados",
            }),

            "indicacao_raiox": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descreva a indicação clínica para o Raio-X. Ex: trauma, dor torácica, queda, suspeita de fratura...",
            }),

            "indicacao_tomografia": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descreva a indicação clínica para a Tomografia. Ex: trauma craniano, AVC, dor abdominal, dispneia...",
            }),

            "indicacao_outros_imagem": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descreva a indicação clínica para mamografia, densitometria ou outros exames de imagem.",
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

            "receita": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Receita medica",
            }),

            "atestado": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Texto do atestado medico",
            }),

            "atestado_dias": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "placeholder": "Ex: 3",
            }),

            "atestado_cid": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "off",
                "placeholder": "Digite o codigo ou nome do CID",
            }),
        }


class ReavaliacaoMedicaForm(forms.ModelForm):

    class Meta:
        model = ReavaliacaoMedica

        fields = [
            "medico_responsavel",
            "crm_medico",
            "cid",
            "avaliacao",
            "conduta",
            "orientacoes",
        ]

        widgets = {
            "medico_responsavel": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do medico que esta reavaliando",
            }),

            "crm_medico": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CRM",
            }),

            "cid": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CID, se necessario",
            }),

            "avaliacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Registre a avaliacao atual, evolucao do quadro, resultados analisados e decisao clinica.",
            }),

            "conduta": forms.Select(attrs={
                "class": "form-select",
            }),

            "orientacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Orientacoes, alta, retorno, sinais de alarme ou continuidade do cuidado.",
            }),
        }
