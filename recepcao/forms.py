from django import forms
from .models import Recepcao


class RecepcaoForm(forms.ModelForm):

    class Meta:

        model = Recepcao

        fields = "__all__"
    
    def save(self, commit=True):
        return super().save(commit=commit)

    def clean(self):
        cleaned_data = super().clean()
        idade = cleaned_data.get("idade")

        if idade is not None and idade < 18:
            nome_responsavel = (cleaned_data.get("nome_responsavel") or "").strip()
            cpf_responsavel = (cleaned_data.get("cpf_responsavel") or "").strip()

            if not nome_responsavel:
                self.add_error(
                    "nome_responsavel",
                    "Informe o nome do responsável para criança/adolescente."
                )

            if not cpf_responsavel:
                self.add_error(
                    "cpf_responsavel",
                    "Informe o CPF do responsável para criança/adolescente."
                )

        return cleaned_data
    
    email = forms.EmailField(
    required=False,
    widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "exemplo@email.com",
    })
)
