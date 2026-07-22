from django import forms

from accounts.forms import CARGO_FUNCAO_CHOICES, cargo_funcao_valores
from accounts.models import Usuario
from accounts.utils import CONSELHO_PADRAO_POR_CARGO

from .models import (
    EscalaFuncionario,
    Funcionario,
    VinculoFuncionario,
    resolver_cadastro,
)


class FuncionarioForm(forms.ModelForm):
    cargo = forms.ChoiceField(
        choices=CARGO_FUNCAO_CHOICES,
        required=False,
        label="Cargo ou funcao",
    )

    class Meta:
        model = Funcionario
        fields = [
            "usuario",
            "nome",
            "cpf",
            "matricula",
            "cargo",
            "funcao",
            "setor",
            "unidade",
            "conselho_profissional",
            "registro_profissional",
            "telefone",
            "email",
            "data_admissao",
            "data_demissao",
            "tipo_vinculo",
            "carga_horaria_semanal",
            "ativo",
            "observacoes",
        ]
        widgets = {
            "data_admissao": forms.DateInput(attrs={"type": "date"}),
            "data_demissao": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["usuario"].queryset = Usuario.objects.order_by("first_name", "username")
        self.fields["usuario"].required = False
        self.fields["unidade"].required = False
        self.fields["email"].required = False
        self.fields["ativo"].required = False

        cargo_atual = self.initial.get("cargo") or getattr(self.instance, "cargo", "")
        if cargo_atual and cargo_atual not in cargo_funcao_valores():
            self.fields["cargo"].choices = [
                *CARGO_FUNCAO_CHOICES,
                ("Cargo salvo anteriormente", ((cargo_atual, f"{cargo_atual} (atual)"),)),
            ]

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get("usuario")
        cargo = cleaned_data.get("cargo") or ""
        conselho = cleaned_data.get("conselho_profissional") or ""
        registro = (cleaned_data.get("registro_profissional") or "").strip()
        data_admissao = cleaned_data.get("data_admissao")
        data_demissao = cleaned_data.get("data_demissao")

        if usuario:
            qs = Funcionario.objects.filter(usuario=usuario)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("usuario", "Este login ja esta vinculado a outro funcionario.")

        if not conselho and cargo in CONSELHO_PADRAO_POR_CARGO:
            conselho = CONSELHO_PADRAO_POR_CARGO[cargo]
            cleaned_data["conselho_profissional"] = conselho

        if conselho and not registro:
            self.add_error("registro_profissional", "Informe o numero do conselho profissional.")

        if registro and not conselho:
            self.add_error("conselho_profissional", "Selecione o conselho regional.")

        if data_admissao and data_demissao and data_demissao < data_admissao:
            self.add_error(
                "data_demissao",
                "A data de demissao nao pode ser menor que a data de admissao.",
            )

        cleaned_data["registro_profissional"] = registro
        return cleaned_data

    def save(self, commit=True):
        funcionario = super().save(commit=False)
        if funcionario.data_demissao:
            funcionario.ativo = False

        if commit:
            funcionario.save()
            self.sync_usuario(funcionario)
            self.sync_vinculo_atual(funcionario)

        return funcionario

    def sync_vinculo_atual(self, funcionario):
        if not funcionario.data_admissao:
            return

        VinculoFuncionario.objects.update_or_create(
            funcionario=funcionario,
            data_admissao=funcionario.data_admissao,
            defaults={
                "data_demissao": funcionario.data_demissao,
                "tipo_vinculo_ref": funcionario.tipo_vinculo_ref,
                "tipo_vinculo": funcionario.tipo_vinculo,
                "cargo_ref": funcionario.cargo_ref,
                "cargo": funcionario.cargo,
                "setor_ref": funcionario.setor_ref,
                "setor": funcionario.setor,
                "unidade": funcionario.unidade,
                "observacoes": "Vinculo atualizado pelo cadastro do funcionario.",
            },
        )

    def sync_usuario(self, funcionario):
        usuario = funcionario.usuario
        if not usuario:
            return

        partes = funcionario.nome.split()
        usuario.first_name = partes[0] if partes else funcionario.nome
        usuario.last_name = " ".join(partes[1:]) if len(partes) > 1 else ""
        usuario.email = funcionario.email
        usuario.cargo_ref = funcionario.cargo_ref
        usuario.funcao_ref = funcionario.funcao_ref
        usuario.cargo = funcionario.cargo
        usuario.unidade = funcionario.unidade
        usuario.conselho_ref = funcionario.conselho_ref
        usuario.conselho_profissional = funcionario.conselho_profissional
        usuario.registro_profissional = funcionario.registro_profissional
        usuario.is_active = funcionario.ativo
        usuario.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
                "cargo_ref",
                "funcao_ref",
                "cargo",
                "unidade",
                "conselho_ref",
                "conselho_profissional",
                "registro_profissional",
                "is_active",
            ]
        )


class EscalaFuncionarioForm(forms.ModelForm):
    class Meta:
        model = EscalaFuncionario
        fields = [
            "funcionario",
            "data",
            "turno",
            "hora_inicio",
            "hora_fim",
            "setor",
            "status",
            "observacoes",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        funcionario = kwargs.pop("funcionario", None)
        super().__init__(*args, **kwargs)

        self.fields["funcionario"].queryset = Funcionario.objects.filter(
            ativo=True
        ).order_by("nome")

        if funcionario:
            self.fields["funcionario"].initial = funcionario
            self.fields["funcionario"].widget = forms.HiddenInput()

        for field in self.fields.values():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")

        if hora_inicio and hora_fim and hora_fim <= hora_inicio:
            self.add_error("hora_fim", "A hora final deve ser maior que a hora inicial.")

        return cleaned_data

    def save(self, commit=True):
        escala = super().save(commit=False)

        if escala.setor and not escala.setor_ref_id:
            escala.setor_ref = resolver_cadastro("SetorHospitalar", escala.setor)

        if commit:
            escala.save()

        return escala


class VinculoFuncionarioForm(forms.ModelForm):
    class Meta:
        model = VinculoFuncionario
        fields = [
            "data_admissao",
            "data_demissao",
            "tipo_vinculo",
            "cargo",
            "setor",
            "unidade",
            "motivo_demissao",
            "observacoes",
        ]
        widgets = {
            "data_admissao": forms.DateInput(attrs={"type": "date"}),
            "data_demissao": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        self.funcionario = kwargs.pop("funcionario", None)
        super().__init__(*args, **kwargs)

        if self.funcionario and not self.is_bound:
            self.fields["cargo"].initial = self.funcionario.cargo
            self.fields["setor"].initial = self.funcionario.setor
            self.fields["unidade"].initial = self.funcionario.unidade
            self.fields["tipo_vinculo"].initial = self.funcionario.tipo_vinculo

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        data_admissao = cleaned_data.get("data_admissao")
        data_demissao = cleaned_data.get("data_demissao")

        if data_admissao and data_demissao and data_demissao < data_admissao:
            self.add_error(
                "data_demissao",
                "A data de demissao nao pode ser menor que a data de admissao.",
            )

        return cleaned_data

    def save(self, commit=True):
        vinculo = super().save(commit=False)

        if vinculo.tipo_vinculo and not vinculo.tipo_vinculo_ref_id:
            vinculo.tipo_vinculo_ref = resolver_cadastro(
                "TipoVinculoTrabalho",
                vinculo.tipo_vinculo,
            )

        if vinculo.cargo and not vinculo.cargo_ref_id:
            vinculo.cargo_ref = resolver_cadastro("CargoProfissional", vinculo.cargo)

        if vinculo.setor and not vinculo.setor_ref_id:
            vinculo.setor_ref = resolver_cadastro("SetorHospitalar", vinculo.setor)

        if commit:
            vinculo.save()

        return vinculo
