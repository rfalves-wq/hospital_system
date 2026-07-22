PAINEIS_PADRAO = [
    {
        "codigo": "acolhimento",
        "nome": "Acolhimento",
        "descricao": "Entrada e tipo de atendimento do paciente",
        "ordem": 10,
        "prefixos": ["acolhimento/"],
    },
    {
        "codigo": "recepcao",
        "nome": "Recepcao",
        "descricao": "Cadastro, recepcao e encaminhamento do paciente",
        "ordem": 20,
        "prefixos": ["recepcao/"],
    },
    {
        "codigo": "classificacao",
        "nome": "Classificacao de risco",
        "descricao": "Classificacao de risco e chamadas do setor",
        "ordem": 30,
        "prefixos": ["classificacao/"],
    },
    {
        "codigo": "medico",
        "nome": "Medico",
        "descricao": "Fila medica, consulta e retorno",
        "ordem": 40,
        "prefixos": ["medico/"],
    },
    {
        "codigo": "prontuario",
        "nome": "Prontuario",
        "descricao": "Consulta do prontuario do paciente",
        "ordem": 50,
        "prefixos": ["prontuario/"],
    },
    {
        "codigo": "medicacao",
        "nome": "Sala de medicacao",
        "descricao": "Administracao de medicacoes",
        "ordem": 60,
        "prefixos": ["medicacao/"],
    },
    {
        "codigo": "farmacia",
        "nome": "Farmacia",
        "descricao": "Estoque, farmacia e dispensacao",
        "ordem": 70,
        "prefixos": ["farmacia/"],
    },
    {
        "codigo": "internacao",
        "nome": "Internacao",
        "descricao": "Leitos, internacao e acompanhamento",
        "ordem": 80,
        "prefixos": ["internacao/"],
    },
    {
        "codigo": "laboratorio",
        "nome": "Laboratorio",
        "descricao": "Solicitacoes e resultados laboratoriais",
        "ordem": 90,
        "prefixos": ["laboratorio/"],
    },
    {
        "codigo": "imagem",
        "nome": "Imagem",
        "descricao": "Exames de imagem e resultados",
        "ordem": 100,
        "prefixos": ["imagem/"],
    },
    {
        "codigo": "ti",
        "nome": "Tecnologia da Informacao",
        "descricao": "Equipamentos, rede e chamados do TI",
        "ordem": 110,
        "prefixos": ["tecnologia/", "tecnologia/chamados/", "tecnologia/status/"],
    },
    {
        "codigo": "suporte_ti",
        "nome": "Solicitar TI",
        "descricao": "Abrir e acompanhar chamados para a area de TI",
        "ordem": 120,
        "prefixos": ["tecnologia/pedido-servico/"],
    },
    {
        "codigo": "painel_chamados",
        "nome": "Painel de chamados",
        "descricao": "Painel publico de chamadas de pacientes",
        "ordem": 130,
        "prefixos": ["painel/"],
    },
    {
        "codigo": "ambulancia",
        "nome": "Solicitacao de Ambulancia",
        "descricao": "Remocao, transferencia e transporte de pacientes",
        "ordem": 140,
        "prefixos": ["ambulancia/"],
    },
    {
        "codigo": "auditoria",
        "nome": "Auditoria do Sistema",
        "descricao": "Logs, rastreabilidade e conferencias de acoes",
        "ordem": 150,
        "prefixos": ["auditoria/"],
    },
    {
        "codigo": "funcionarios",
        "nome": "Funcionarios",
        "descricao": "Cadastro, conselho, setores e escala de profissionais",
        "ordem": 160,
        "prefixos": ["funcionarios/"],
    },
    {
        "codigo": "relatorios",
        "nome": "Relatorios",
        "descricao": "Indicadores gerenciais e exportacao de dados",
        "ordem": 170,
        "prefixos": ["relatorios/"],
    },
    {
        "codigo": "almoxarifado",
        "nome": "Almoxarifado",
        "descricao": "Materiais, suprimentos e movimentacao de estoque",
        "ordem": 180,
        "prefixos": ["almoxarifado/"],
    },
    {
        "codigo": "ouvidoria",
        "nome": "Ouvidoria / SAC",
        "descricao": "Manifestacoes, ocorrencias, prazos e respostas",
        "ordem": 190,
        "prefixos": ["ouvidoria/"],
    },
]

PAINEL_CHOICES = [
    (painel["codigo"], painel["nome"])
    for painel in PAINEIS_PADRAO
]

PAINEIS_TODOS = {codigo for codigo, _nome in PAINEL_CHOICES}

PREFIXOS_POR_PAINEL = sorted(
    [
        (prefixo, painel["codigo"])
        for painel in PAINEIS_PADRAO
        for prefixo in painel["prefixos"]
    ],
    key=lambda item: len(item[0]),
    reverse=True,
)


def painel_por_caminho(path):
    caminho = (path or "").lstrip("/")

    for prefixo, codigo in PREFIXOS_POR_PAINEL:
        if caminho.startswith(prefixo):
            return codigo

    return ""


def usuario_codigos_paineis(user):
    if not user or not user.is_authenticated:
        return set()

    cache_attr = "_hospital_codigos_paineis"
    if hasattr(user, cache_attr):
        return getattr(user, cache_attr)

    if user.is_superuser or user.is_staff:
        codigos = set(PAINEIS_TODOS)
        setattr(user, cache_attr, codigos)
        return codigos

    codigos = set(
        user.paineis_extra
        .filter(ativo=True)
        .values_list("codigo", flat=True)
    )
    codigos.update(
        user.perfis_acesso
        .filter(ativo=True)
        .values_list("paineis__codigo", flat=True)
    )
    codigos.discard(None)

    setattr(user, cache_attr, codigos)
    return codigos


def usuario_tem_painel(user, codigo):
    if not codigo:
        return True

    codigos = usuario_codigos_paineis(user)

    if codigo == "suporte_ti" and "ti" in codigos:
        return True

    return codigo in codigos


def mapa_paineis_usuario(user):
    codigos = usuario_codigos_paineis(user)

    return {
        codigo: codigo in codigos or (codigo == "suporte_ti" and "ti" in codigos)
        for codigo, _nome in PAINEL_CHOICES
    }
