from django import forms

from .models import EquipamentoTI, normalizar_mac


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
