# Normalizacao do Banco de Dados

Este documento registra a primeira etapa de normalizacao do sistema hospitalar.
As tabelas antigas foram mantidas quando ainda existem telas usando os campos
originais, para evitar perda de dados e quebra de fluxo.

## 1FN

Regra aplicada: cada campo deve guardar um unico valor atomico.

Implementado:
- Documentos medicos sairam de colunas soltas da consulta para
  `medico.DocumentoConsultaMedica`.
- Equipe e equipamentos da ambulancia ganharam tabelas proprias:
  `ambulancia.MembroEquipeAmbulancia`,
  `ambulancia.EquipamentoMedicoAmbulancia` e
  `ambulancia.EquipamentoSolicitacaoAmbulancia`.
- Leitos passaram a existir como linhas em `internacao.LeitoInternacao`.

## 2FN

Regra aplicada: dados dependem da chave inteira da tabela, nao de parte dela.

Implementado:
- Relacoes muitos-para-muitos e listas foram separadas em tabelas de ligacao.
- Equipamento de ambulancia fica em catalogo e a quantidade/conferencia fica na
  tabela da solicitacao.
- Funcao profissional passou a se relacionar com cargo e setor padrao.

## 3FN

Regra aplicada: campos nao devem depender de outros campos nao-chave.

Implementado:
- Criado app `cadastros` para dados de referencia:
  `ConselhoProfissional`, `SetorHospitalar`, `CargoProfissional`,
  `FuncaoProfissional` e `TipoVinculoTrabalho`.
- `accounts.Usuario` e `funcionarios.Funcionario` ganharam referencias
  normalizadas para cargo, funcao, conselho, setor e tipo de vinculo.

## 4FN

Regra aplicada: conjuntos independentes nao ficam misturados na mesma tabela.

Implementado:
- Em ambulancia, equipe e equipamentos foram separados da solicitacao principal.
- Em consulta medica, documentos clinicos ficaram separados da consulta.

## 5FN

Regra aplicada: fatos compostos ficam decompostos em relacoes menores sem perder
capacidade de recompor a informacao.

Implementado:
- Leito = setor + codigo + tipo + status operacional.
- Documento medico = consulta + tipo + conteudo + profissional + CID quando
  existir.
- Solicitacao de ambulancia = solicitacao + membros da equipe + equipamentos.

## Campos legados mantidos

Alguns campos de texto foram mantidos temporariamente porque ainda sao usados por
telas existentes:
- `Usuario.cargo`, `Usuario.conselho_profissional`.
- `Funcionario.cargo`, `Funcionario.funcao`, `Funcionario.setor`.
- `Internacao.leito`, `Internacao.setor`.
- Campos de texto antigos da consulta medica e ambulancia.

Esses campos sao sincronizados com as novas tabelas sempre que possivel. A etapa
seguinte e alterar as telas para gravarem diretamente nas tabelas normalizadas e,
depois de validar os dados, remover os campos legados.
