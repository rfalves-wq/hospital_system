import json
from decimal import Decimal, InvalidOperation

from django import forms

from medico.models import ConsultaMedica

from .models import MedicamentoEstoque, MovimentacaoEstoque


class FarmaciaForm(forms.ModelForm):
    itens_estoque_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            "id": "id_itens_estoque_json",
        })
    )

    class Meta:
        model = ConsultaMedica

        fields = [
            "medicamentos_dispensados",
            "quantidade_farmacia",
            "lote_farmacia",
            "validade_farmacia",
            "observacao_farmacia",
            "profissional_farmacia_nome",
            "profissional_farmacia_registro",
        ]

        widgets = {
            "medicamentos_dispensados": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Descreva os medicamentos separados/liberados pela farmácia.",
            }),

            "quantidade_farmacia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 1 ampola, 2 comprimidos, 500 ml...",
            }),

            "lote_farmacia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Lote do medicamento, se houver",
            }),

            "validade_farmacia": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "observacao_farmacia": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Observações da farmácia, substituições, falta de item ou orientação para enfermagem.",
            }),

            "profissional_farmacia_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do profissional da farmácia",
            }),

            "profissional_farmacia_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro, matrícula ou identificação",
            }),
        }

    def __init__(self, *args, exigir_itens_estoque=False, **kwargs):
        self.exigir_itens_estoque = exigir_itens_estoque
        self.itens_estoque = []

        super().__init__(*args, **kwargs)

        self.fields["medicamentos_dispensados"].label = "Medicamentos dispensados"
        self.fields["quantidade_farmacia"].label = "Quantidade dispensada"
        self.fields["lote_farmacia"].label = "Lote"
        self.fields["validade_farmacia"].label = "Validade"
        self.fields["observacao_farmacia"].label = "Observações da farmácia"
        self.fields["profissional_farmacia_nome"].label = "Nome do profissional"
        self.fields["profissional_farmacia_registro"].label = "Registro / Matrícula"

        self.fields["medicamentos_dispensados"].required = True
        self.fields["quantidade_farmacia"].required = True
        self.fields["profissional_farmacia_nome"].required = True
        self.fields["profissional_farmacia_registro"].required = True

        if self.instance and self.instance.pk:
            if self.instance.prescricao and not self.instance.medicamentos_dispensados:
                self.initial["medicamentos_dispensados"] = self.instance.prescricao

    def clean_itens_estoque_json(self):
        valor = self.cleaned_data.get("itens_estoque_json", "").strip()

        if not valor:
            if self.exigir_itens_estoque:
                raise forms.ValidationError(
                    "Selecione pelo menos um medicamento do estoque para dar baixa."
                )

            self.itens_estoque = []
            return valor

        try:
            dados = json.loads(valor)
        except json.JSONDecodeError:
            raise forms.ValidationError(
                "Lista de medicamentos do estoque invalida."
            )

        if not isinstance(dados, list):
            raise forms.ValidationError(
                "Lista de medicamentos do estoque invalida."
            )

        itens = []

        for item in dados:
            try:
                medicamento_id = int(item.get("medicamento_id"))
                quantidade = Decimal(str(item.get("quantidade", "0")).replace(",", "."))
            except (TypeError, ValueError, InvalidOperation):
                raise forms.ValidationError(
                    "Verifique as quantidades dos medicamentos selecionados."
                )

            if medicamento_id <= 0 or quantidade <= 0:
                raise forms.ValidationError(
                    "Todos os medicamentos selecionados precisam ter quantidade maior que zero."
                )

            itens.append({
                "medicamento_id": medicamento_id,
                "quantidade": quantidade,
            })

        if self.exigir_itens_estoque and not itens:
            raise forms.ValidationError(
                "Selecione pelo menos um medicamento do estoque para dar baixa."
            )

        self.itens_estoque = itens
        return valor


class MedicamentoEstoqueForm(forms.ModelForm):

    class Meta:
        model = MedicamentoEstoque

        fields = [
            "nome",
            "categoria",
            "metodo_aplicacao",
            "principio_ativo",
            "apresentacao",
            "concentracao",
            "unidade_medida",
            "estoque_atual",
            "estoque_minimo",
            "localizacao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome comercial ou nome do medicamento",
            }),
            "categoria": forms.Select(attrs={
                "class": "form-select",
            }),
            "metodo_aplicacao": forms.Select(attrs={
                "class": "form-select",
            }),
            "principio_ativo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Princípio ativo",
            }),
            "apresentacao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: comprimido, ampola, frasco, bolsa",
            }),
            "concentracao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 500 mg, 1 g/2 ml, 0,9%",
            }),
            "unidade_medida": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: unidade, ampola, ml, frasco",
            }),
            "estoque_atual": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "estoque_minimo": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "localizacao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: armário 1, prateleira B, geladeira",
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class MovimentacaoEstoqueForm(forms.ModelForm):

    class Meta:
        model = MovimentacaoEstoque

        fields = [
            "quantidade",
            "lote",
            "validade",
            "origem_destino",
            "profissional_nome",
            "profissional_registro",
            "observacao",
        ]

        widgets = {
            "quantidade": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
            }),
            "lote": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Lote, se houver",
            }),
            "validade": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "origem_destino": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Fornecedor, setor, paciente, perda ou inventário",
            }),
            "profissional_nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do profissional",
            }),
            "profissional_registro": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registro ou matrícula",
            }),
            "observacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Observações da movimentação",
            }),
        }

    def __init__(self, *args, tipo_movimento=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.tipo_movimento = tipo_movimento

        if tipo_movimento == MovimentacaoEstoque.AJUSTE:
            self.fields["quantidade"].label = "Novo saldo do estoque"
        else:
            self.fields["quantidade"].label = "Quantidade"

        if tipo_movimento == MovimentacaoEstoque.ENTRADA:
            self.fields["origem_destino"].label = "Origem"
            self.fields["origem_destino"].widget.attrs["placeholder"] = "Ex: fornecedor, compra, transferência"
        elif tipo_movimento == MovimentacaoEstoque.SAIDA:
            self.fields["origem_destino"].label = "Destino"
            self.fields["origem_destino"].widget.attrs["placeholder"] = "Ex: paciente, setor, perda, vencimento"
        else:
            self.fields["origem_destino"].label = "Motivo do ajuste"
            self.fields["origem_destino"].widget.attrs["placeholder"] = "Ex: inventário, correção de saldo"
