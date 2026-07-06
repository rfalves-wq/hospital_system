from django import forms

from medico.models import ConsultaMedica


class MedicacaoForm(forms.ModelForm):

    class Meta:
        model = ConsultaMedica

        fields = [
            "medicamento_utilizado",
            "dose_medicacao",
            "via_medicacao",
            "horario_medicacao",
            "lote_medicacao",
            "quantidade_medicacao",
            "materiais_utilizados_medicacao",
            "medicacao_administrada",
            "observacoes_medicacao",
            "profissional_medicacao_nome",
            "profissional_medicacao_registro",
        ]

        widgets = {
            "medicamento_utilizado": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descreva o medicamento utilizado. Ex: Dipirona, Soro fisiológico, Ceftriaxona...",
            }),

            "dose_medicacao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 1g, 500mg, 10ml...",
            }),

            "via_medicacao": forms.Select(attrs={
                "class": "form-select",
            }, choices=[
                ("", "Selecione"),
                ("VO", "VO - Via oral"),
                ("EV", "EV - Endovenosa"),
                ("IM", "IM - Intramuscular"),
                ("SC", "SC - Subcutânea"),
                ("SL", "SL - Sublingual"),
                ("INALATORIA", "Inalatória"),
                ("TOPICA", "Tópica"),
                ("RETAL", "Retal"),
                ("OCULAR", "Ocular"),
                ("NASAL", "Nasal"),
                ("OUTRA", "Outra"),
            ]),

            "horario_medicacao": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),

            "lote_medicacao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Lote do medicamento, se houver",
            }),

            "quantidade_medicacao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Quantidade utilizada",
            }),

            "materiais_utilizados_medicacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ex: equipo, seringa, agulha, cateter, soro, diluente...",
            }),

            "medicacao_administrada": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Resumo da medicação administrada, dose, via e horário.",
            }),

            "observacoes_medicacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Observações, intercorrências ou reações do paciente.",
            }),

            "profissional_medicacao_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do profissional responsável",
            }),

            "profissional_medicacao_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "COREN, matrícula ou registro",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        obrigatorios = [
            "medicamento_utilizado",
            "dose_medicacao",
            "via_medicacao",
            "horario_medicacao",
            "quantidade_medicacao",
            "medicacao_administrada",
            "profissional_medicacao_nome",
            "profissional_medicacao_registro",
        ]

        for campo in obrigatorios:
            self.fields[campo].required = True

        opcionais = [
            "lote_medicacao",
            "materiais_utilizados_medicacao",
            "observacoes_medicacao",
        ]

        for campo in opcionais:
            self.fields[campo].required = False