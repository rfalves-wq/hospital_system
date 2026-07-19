from datetime import timedelta

from django import forms
from django.db.models import Q
from django.utils import timezone

from acolhimento.models import Acolhimento
from .models import SolicitacaoAmbulancia


class SolicitacaoAmbulanciaForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoAmbulancia
        fields = [
            "acolhimento",
            "nome_paciente",
            "numero_bam",
            "cpf",
            "data_nascimento",
            "tipo_transporte",
            "prioridade",
            "origem",
            "destino",
            "unidade_destino",
            "motivo",
            "resumo_clinico",
            "necessita_maca",
            "necessita_oxigenio",
            "necessita_isolamento",
            "acompanhante",
            "setor_solicitante",
            "contato",
            "observacoes",
        ]
        widgets = {
            "acolhimento": forms.Select(attrs={"class": "form-select"}),
            "nome_paciente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome completo do paciente",
            }),
            "numero_bam": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "BAM",
            }),
            "cpf": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "000.000.000-00",
            }),
            "data_nascimento": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "tipo_transporte": forms.Select(attrs={"class": "form-select"}),
            "prioridade": forms.Select(attrs={"class": "form-select"}),
            "origem": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Emergencia, Internacao, Observacao",
            }),
            "destino": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Local de destino",
            }),
            "unidade_destino": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Hospital, clinica ou setor de destino",
            }),
            "motivo": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Motivo da remocao ou transferencia",
            }),
            "resumo_clinico": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Resumo clinico importante para o transporte",
            }),
            "setor_solicitante": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Setor solicitante",
            }),
            "contato": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ramal, telefone ou responsavel",
            }),
            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Observacoes para equipe de transporte",
            }),
            "necessita_maca": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "necessita_oxigenio": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "necessita_isolamento": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "acompanhante": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        limite = timezone.now() - timedelta(days=15)
        acolhimento_id = ""

        if self.is_bound:
            acolhimento_id = self.data.get(self.add_prefix("acolhimento"), "")
        elif self.instance and self.instance.acolhimento_id:
            acolhimento_id = str(self.instance.acolhimento_id)

        filtro = Q(data_acolhimento__gte=limite)
        if acolhimento_id:
            filtro |= Q(pk=acolhimento_id)

        self.fields["acolhimento"].queryset = (
            Acolhimento.objects
            .filter(filtro)
            .order_by("-data_acolhimento")
        )
        self.fields["acolhimento"].required = False
        self.fields["acolhimento"].empty_label = "Selecionar paciente do sistema"
        self.fields["nome_paciente"].required = False
        self.fields["numero_bam"].required = False
        self.fields["cpf"].required = False
        self.fields["data_nascimento"].required = False
        self.fields["unidade_destino"].required = False
        self.fields["resumo_clinico"].required = False
        self.fields["observacoes"].required = False
        self.fields["setor_solicitante"].required = False
        self.fields["contato"].required = False

    def clean(self):
        cleaned_data = super().clean()
        acolhimento = cleaned_data.get("acolhimento")
        nome = (cleaned_data.get("nome_paciente") or "").strip()

        if acolhimento:
            cleaned_data["nome_paciente"] = acolhimento.nome_paciente or nome
            cleaned_data["numero_bam"] = acolhimento.numero_bam or cleaned_data.get("numero_bam") or ""
            cleaned_data["cpf"] = acolhimento.cpf or cleaned_data.get("cpf") or ""
            cleaned_data["data_nascimento"] = (
                acolhimento.data_nascimento or cleaned_data.get("data_nascimento")
            )
        elif not nome:
            self.add_error(
                "nome_paciente",
                "Informe o paciente ou selecione um atendimento.",
            )

        return cleaned_data


class DadosTransporteAmbulanciaForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoAmbulancia
        fields = [
            "motorista",
            "responsavel_transporte",
            "veiculo",
            "placa",
            "medico_transporte",
            "enfermeiro_transporte",
            "tecnico_transporte",
            "equipamentos_medicos",
            "km_saida",
            "combustivel_saida",
            "km_chegada",
            "combustivel_chegada",
            "checklist_saida",
            "condicao_paciente_saida",
            "condicao_paciente_chegada",
            "ocorrencias_transporte",
            "recebedor_destino",
        ]

    def clean(self):
        cleaned_data = super().clean()
        km_saida = cleaned_data.get("km_saida")
        km_chegada = cleaned_data.get("km_chegada")

        if km_saida is not None and km_chegada is not None and km_chegada < km_saida:
            self.add_error(
                "km_chegada",
                "A quilometragem de chegada nao pode ser menor que a de saida.",
            )

        return cleaned_data
