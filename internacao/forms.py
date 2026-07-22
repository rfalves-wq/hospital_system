from django import forms

from .models import (
    EvolucaoInternacao,
    Internacao,
    LeitoInternacao,
    SetorInternacao,
)


class SetorInternacaoForm(forms.ModelForm):
    class Meta:
        model = SetorInternacao
        fields = ["nome", "codigo", "ativo", "ordem"]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Clinica medica",
            }),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: CLINICA_MEDICA",
            }),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ordem": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["codigo"].required = False

    def clean_codigo(self):
        return (self.cleaned_data.get("codigo") or "").strip().upper()


class LeitoInternacaoForm(forms.ModelForm):
    class Meta:
        model = LeitoInternacao
        fields = [
            "setor",
            "codigo",
            "tipo",
            "status_operacional",
            "observacao",
            "ordem",
        ]
        widgets = {
            "setor": forms.Select(attrs={"class": "form-select"}),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: CM-01",
            }),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "status_operacional": forms.Select(attrs={"class": "form-select"}),
            "observacao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: proximo ao posto, isolamento, manutencao",
            }),
            "ordem": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["setor"].queryset = SetorInternacao.objects.order_by(
            "ordem",
            "nome",
        )

    def clean_codigo(self):
        return (self.cleaned_data.get("codigo") or "").strip().upper()


class InternacaoForm(forms.ModelForm):
    class Meta:
        model = Internacao
        fields = [
            "leito",
            "setor",
            "diagnostico_admissao",
            "cuidados",
            "profissional_responsavel",
            "profissional_responsavel_registro",
            "observacoes",
        ]
        widgets = {
            "leito": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: A-12, Enfermaria 03, Isolamento 01",
            }),
            "setor": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Clínica médica, observação, isolamento",
            }),
            "diagnostico_admissao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Diagnóstico ou motivo da internação",
            }),
            "cuidados": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Cuidados iniciais, dieta, repouso, monitorização...",
            }),
            "profissional_responsavel": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Profissional responsável pela admissão",
            }),
            "profissional_responsavel_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CRM, COREN ou registro",
            }),
            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observações adicionais",
            }),
        }


class EvolucaoInternacaoForm(forms.ModelForm):
    class Meta:
        model = EvolucaoInternacao
        fields = [
            "pressao_arterial",
            "temperatura",
            "pulso",
            "frequencia_respiratoria",
            "saturacao",
            "evolucao",
            "conduta",
            "profissional",
            "profissional_registro",
        ]
        widgets = {
            "pressao_arterial": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 120x80",
            }),
            "temperatura": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.1",
                "placeholder": "°C",
            }),
            "pulso": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "bpm",
            }),
            "frequencia_respiratoria": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "irpm",
            }),
            "saturacao": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "%",
            }),
            "evolucao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Evolução clínica do paciente",
            }),
            "conduta": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Conduta, cuidados e próximas ações",
            }),
            "profissional": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Profissional que registrou a evolução",
            }),
            "profissional_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CRM, COREN ou registro",
            }),
        }


class AltaInternacaoForm(forms.ModelForm):
    class Meta:
        model = Internacao
        fields = [
            "resumo_alta",
            "profissional_alta",
            "profissional_alta_registro",
        ]
        widgets = {
            "resumo_alta": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Resumo da alta, orientações e destino do paciente",
            }),
            "profissional_alta": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Profissional responsável pela alta",
            }),
            "profissional_alta_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CRM, COREN ou registro",
            }),
        }
