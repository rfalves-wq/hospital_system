from django import forms
from django.contrib.auth import password_validation

from .models import PainelSistema, PerfilAcesso, Usuario

class LoginForm(forms.Form):

    username = forms.CharField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )


class UsuarioSistemaForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Digite a senha",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Repita a senha",
            }
        ),
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "cargo",
            "unidade",
            "is_active",
            "is_staff",
            "is_superuser",
            "perfis_acesso",
            "paineis_extra",
        ]
        labels = {
            "username": "Usuario de login",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
            "cargo": "Cargo ou funcao",
            "unidade": "Unidade",
            "is_active": "Usuario ativo",
            "is_staff": "Pode gerenciar usuarios",
            "is_superuser": "Administrador geral",
            "perfis_acesso": "Categorias de acesso",
            "paineis_extra": "Paineis extras",
        }
        help_texts = {
            "username": "",
            "is_staff": "Libera a area de Login e Seguranca.",
            "is_superuser": "Acesso completo ao sistema.",
            "paineis_extra": "Use quando o usuario precisar de um painel fora da categoria.",
        }
        widgets = {
            "perfis_acesso": forms.CheckboxSelectMultiple(),
            "paineis_extra": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        self.fields["perfis_acesso"].queryset = PerfilAcesso.objects.filter(
            ativo=True
        ).prefetch_related("paineis")
        self.fields["paineis_extra"].queryset = PainelSistema.objects.filter(
            ativo=True
        )
        self.fields["perfis_acesso"].required = False
        self.fields["paineis_extra"].required = False
        self.fields["unidade"].required = False
        self.fields["email"].required = False
        self.fields["cargo"].required = False

        if not self.instance.pk:
            self.fields["password1"].required = True
            self.fields["password2"].required = True
            self.fields["is_active"].initial = True

        if self.request_user and not self.request_user.is_superuser:
            self.fields["is_superuser"].disabled = True
            self.fields["is_superuser"].help_text = (
                "Somente um administrador geral pode alterar esta permissao."
            )

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "security-checkbox"
            elif not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs["class"] = "security-input"

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("As senhas nao conferem.")

            password_validation.validate_password(
                password1,
                self.instance if self.instance.pk else None,
            )

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password1")

        if password:
            usuario.set_password(password)

        if self.request_user and usuario.pk == self.request_user.pk:
            usuario.is_active = True
            usuario.is_staff = True
            if self.request_user.is_superuser:
                usuario.is_superuser = True

        if commit:
            usuario.save()
            self.save_m2m()

        return usuario
