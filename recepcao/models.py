from django.db import models


class Recepcao(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    RACA_CHOICES = [
        ('Branca', 'Branca'),
        ('Preta', 'Preta'),
        ('Parda', 'Parda'),
        ('Amarela', 'Amarela'),
        ('Indígena', 'Indígena'),
        ('Não Informado', 'Não Informado'),
    ]

    # ==========================
    # Dados do Paciente
    # ==========================
    nome_completo = models.CharField(max_length=200)
    nome_social = models.CharField(max_length=200, blank=True, null=True)

    cpf = models.CharField(max_length=14, unique=True)
    cns = models.CharField("Cartão Nacional de Saúde", max_length=20, blank=True, null=True)

    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    raca_cor = models.CharField(max_length=20, choices=RACA_CHOICES)

    nascimento = models.DateField()
    idade = models.PositiveIntegerField()

    nacionalidade = models.CharField(max_length=100)

    uf_nascimento = models.CharField("UF de nascimento", max_length=2)
    naturalidade = models.CharField("Cidade de nascimento", max_length=100)

    nome_mae = models.CharField(max_length=200)
    nome_pai = models.CharField(max_length=200, blank=True, null=True)

    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    situacao_rua = models.BooleanField(default=False)

    # ==========================
    # Endereço
    # ==========================
    cep = models.CharField(max_length=9)
    
    municipio = models.CharField(max_length=100)

    bairro = models.CharField(max_length=100)

    logradouro = models.CharField(max_length=200)

    numero = models.CharField(max_length=10)

    complemento = models.CharField(max_length=100, blank=True, null=True)

    # ==========================
    # Responsável
    # ==========================
    nome_responsavel = models.CharField(max_length=200, blank=True, null=True)

    cpf_responsavel = models.CharField(max_length=14, blank=True, null=True)

    nacionalidade_responsavel = models.CharField(max_length=100, blank=True, null=True)

    uf_nascimento_responsavel = models.CharField(max_length=2, blank=True, null=True)

    naturalidade_responsavel = models.CharField(max_length=100, blank=True, null=True)

    # ==========================
    # Controle
    # ==========================
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recepção"
        verbose_name_plural = "Recepções"
        ordering = ["nome_completo"]

    def __str__(self):
        return self.nome_completo