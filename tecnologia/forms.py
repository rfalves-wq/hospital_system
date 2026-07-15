from django import forms

from .models import ChamadoManutencaoTI, EquipamentoTI, normalizar_mac


class RedeScanForm(forms.Form):
    rede = forms.CharField(
        label="Faixa de rede",
        max_length=32,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ex: 192.168.3.0/24 ou 10.0.0.25"
        })
    )


class EquipamentoTIForm(forms.ModelForm):
    class Meta:
        model = EquipamentoTI
        fields = [
            "nome",
            "tipo",
            "setor",
            "endereco_rede",
            "mac_address",
            "origem_ip",
            "ativo",
            "observacao",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Computador da recepcao"
            }),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "setor": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Recepcao, farmacia, laboratorio"
            }),
            "endereco_rede": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "IP ou nome da maquina"
            }),
            "mac_address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Detectado automaticamente ou informe manualmente"
            }),
            "origem_ip": forms.Select(attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observacoes internas"
            }),
        }

    def clean_mac_address(self):
        valor = self.cleaned_data.get("mac_address")
        mac = normalizar_mac(valor)

        if valor and not mac:
            raise forms.ValidationError(
                "Informe um MAC valido. Ex: AA:BB:CC:DD:EE:FF."
            )

        return mac


class PedidoServicoTIForm(forms.ModelForm):
    class Meta:
        model = ChamadoManutencaoTI
        fields = [
            "titulo",
            "setor_solicitante",
            "contato",
            "tipo_servico",
            "equipamento",
            "prioridade",
            "descricao",
        ]
        widgets = {
            "tipo_servico": forms.Select(attrs={"class": "form-select"}),
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Computador da recepcao desligando"
            }),
            "setor_solicitante": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Recepcao, farmacia, laboratorio"
            }),
            "contato": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ramal, telefone, WhatsApp ou e-mail"
            }),
            "equipamento": forms.Select(attrs={"class": "form-select"}),
            "prioridade": forms.Select(attrs={"class": "form-select"}),
            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descreva o que aconteceu, onde fica o dispositivo e desde quando ocorre"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipamento"].queryset = EquipamentoTI.objects.filter(
            ativo=True
        ).order_by("nome")
        self.fields["equipamento"].required = False
        self.fields["equipamento"].empty_label = "Sem equipamento especifico"
        self.fields["tipo_servico"].initial = ChamadoManutencaoTI.MANUTENCAO
        self.fields["setor_solicitante"].required = True
        self.fields["contato"].required = True
        self.fields["descricao"].required = True


class AtendimentoTIForm(forms.ModelForm):
    class Meta:
        model = ChamadoManutencaoTI
        fields = [
            "status",
            "prioridade",
            "resposta_ti",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "prioridade": forms.Select(attrs={"class": "form-select"}),
            "resposta_ti": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Informe ao usuario o andamento ou a solucao"
            }),
        }
