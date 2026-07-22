from django import forms

from accounts.utils import nome_profissional_request, registro_profissional_request

from .models import AndamentoOuvidoria, ManifestacaoOuvidoria


class ManifestacaoOuvidoriaForm(forms.ModelForm):
    class Meta:
        model = ManifestacaoOuvidoria
        fields = [
            "acolhimento",
            "numero_bam",
            "nome_manifestante",
            "cpf_manifestante",
            "telefone",
            "email",
            "paciente_nome",
            "tipo",
            "canal",
            "prioridade",
            "status",
            "setor_envolvido",
            "titulo",
            "relato",
            "providencias",
            "resposta",
            "observacoes_internas",
            "responsavel_nome",
            "responsavel_registro",
            "prazo_resposta",
        ]
        widgets = {
            "prazo_resposta": forms.DateInput(attrs={"type": "date"}),
            "relato": forms.Textarea(attrs={"rows": 5}),
            "providencias": forms.Textarea(attrs={"rows": 3}),
            "resposta": forms.Textarea(attrs={"rows": 3}),
            "observacoes_internas": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields["acolhimento"].required = False
        self.fields["acolhimento"].queryset = self.fields["acolhimento"].queryset.order_by("-data_acolhimento")[:150]

        if request and not self.is_bound and not self.instance.pk:
            self.fields["responsavel_nome"].initial = nome_profissional_request(request)
            self.fields["responsavel_registro"].initial = registro_profissional_request(request)

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        resposta = (cleaned_data.get("resposta") or "").strip()
        titulo = (cleaned_data.get("titulo") or "").strip()
        relato = (cleaned_data.get("relato") or "").strip()

        if status in [ManifestacaoOuvidoria.RESPONDIDA, ManifestacaoOuvidoria.CONCLUIDA] and not resposta:
            self.add_error("resposta", "Informe a resposta antes de marcar como respondida ou concluida.")

        if len(titulo) < 4:
            self.add_error("titulo", "Informe um titulo mais claro.")

        if len(relato) < 8:
            self.add_error("relato", "Descreva melhor a manifestacao.")

        cleaned_data["titulo"] = titulo
        cleaned_data["relato"] = relato
        cleaned_data["resposta"] = resposta
        return cleaned_data


class AndamentoOuvidoriaForm(forms.ModelForm):
    class Meta:
        model = AndamentoOuvidoria
        fields = [
            "status",
            "anotacao",
            "profissional_nome",
            "profissional_registro",
        ]
        widgets = {
            "anotacao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        if request and not self.is_bound:
            self.fields["profissional_nome"].initial = nome_profissional_request(request)
            self.fields["profissional_registro"].initial = registro_profissional_request(request)

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean_anotacao(self):
        anotacao = (self.cleaned_data.get("anotacao") or "").strip()
        if len(anotacao) < 4:
            raise forms.ValidationError("Informe uma anotacao para registrar o andamento.")
        return anotacao
