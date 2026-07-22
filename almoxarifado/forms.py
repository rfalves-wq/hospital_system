from django import forms

from .models import MaterialAlmoxarifado, MovimentacaoAlmoxarifado


class MaterialAlmoxarifadoForm(forms.ModelForm):
    class Meta:
        model = MaterialAlmoxarifado
        fields = [
            "codigo",
            "nome",
            "categoria",
            "descricao",
            "marca",
            "unidade_medida",
            "fornecedor",
            "localizacao",
            "estoque_atual",
            "estoque_minimo",
            "lote_atual",
            "validade",
            "ativo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Codigo interno ou patrimonio"}),
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do material"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "descricao": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: tamanho, modelo, especificacao"}),
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": "Marca, se houver"}),
            "unidade_medida": forms.TextInput(attrs={"class": "form-control", "placeholder": "unidade, pacote, caixa, rolo..."}),
            "fornecedor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Fornecedor principal"}),
            "localizacao": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prateleira, sala, armario..."}),
            "estoque_atual": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "estoque_minimo": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "lote_atual": forms.TextInput(attrs={"class": "form-control", "placeholder": "Lote atual, se houver"}),
            "validade": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MovimentacaoAlmoxarifadoForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoAlmoxarifado
        fields = [
            "quantidade",
            "lote",
            "validade",
            "setor_destino",
            "origem_destino",
            "solicitante_nome",
            "profissional_nome",
            "profissional_registro",
            "observacao",
        ]
        widgets = {
            "quantidade": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1"}),
            "lote": forms.TextInput(attrs={"class": "form-control", "placeholder": "Lote, se houver"}),
            "validade": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "setor_destino": forms.Select(attrs={"class": "form-select"}),
            "origem_destino": forms.TextInput(attrs={"class": "form-control", "placeholder": "Fornecedor, setor, perda ou inventario"}),
            "solicitante_nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Quem solicitou ou recebeu"}),
            "profissional_nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Profissional responsavel"}),
            "profissional_registro": forms.TextInput(attrs={"class": "form-control", "placeholder": "Registro, matricula ou identificacao"}),
            "observacao": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Observacoes da movimentacao"}),
        }

    def __init__(self, *args, tipo_movimento=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.tipo_movimento = tipo_movimento

        if tipo_movimento == MovimentacaoAlmoxarifado.AJUSTE:
            self.fields["quantidade"].label = "Novo saldo do estoque"
            self.fields["quantidade"].widget.attrs["min"] = "0"
            self.fields["origem_destino"].label = "Motivo do ajuste"
            self.fields["origem_destino"].widget.attrs["placeholder"] = "Ex: inventario, correcao, perda"
        elif tipo_movimento == MovimentacaoAlmoxarifado.ENTRADA:
            self.fields["quantidade"].label = "Quantidade de entrada"
            self.fields["origem_destino"].label = "Origem"
            self.fields["origem_destino"].widget.attrs["placeholder"] = "Ex: fornecedor, compra, doacao"
        else:
            self.fields["quantidade"].label = "Quantidade de saida"
            self.fields["origem_destino"].label = "Destino"
            self.fields["origem_destino"].widget.attrs["placeholder"] = "Ex: setor, paciente, perda, manutencao"

    def clean_quantidade(self):
        quantidade = self.cleaned_data["quantidade"]

        if self.tipo_movimento == MovimentacaoAlmoxarifado.AJUSTE:
            if quantidade < 0:
                raise forms.ValidationError("O saldo do estoque nao pode ser negativo.")
        elif quantidade <= 0:
            raise forms.ValidationError("Informe uma quantidade maior que zero.")

        return quantidade
