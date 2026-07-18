(function () {
    function escaparHtml(valor) {
        return String(valor || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function textoOuTraco(valor) {
        if (valor === undefined || valor === null || valor === "") {
            return "-";
        }

        return String(valor);
    }

    function temTexto(valor) {
        return String(valor || "").trim().length > 0;
    }

    function textoLongo(valor) {
        const texto = textoOuTraco(valor);
        return escaparHtml(texto).replace(/\r?\n/g, "<br>");
    }

    function lerJson(id) {
        const script = document.getElementById(id);

        if (!script) {
            return null;
        }

        try {
            return JSON.parse(script.textContent);
        } catch (erro) {
            return null;
        }
    }

    function valorCampo(id, padrao) {
        const campo = document.getElementById(id);
        return campo ? campo.value : (padrao || "");
    }

    function campoMarcado(id, padrao) {
        const campo = document.getElementById(id);
        return campo ? campo.checked : Boolean(padrao);
    }

    function textoSelecionado(id, padrao) {
        const campo = document.getElementById(id);

        if (!campo || campo.selectedIndex < 0) {
            return padrao || "";
        }

        return campo.options[campo.selectedIndex].text;
    }

    function coletarFormulario(base) {
        const dados = Object.assign({}, base || {});

        dados.medicoResponsavel = valorCampo("id_medico_responsavel", dados.medicoResponsavel);
        dados.crmMedico = valorCampo("id_crm_medico", dados.crmMedico);
        dados.cid = valorCampo("id_cid", dados.cid);
        dados.queixaPrincipal = valorCampo("id_queixa_principal", dados.queixaPrincipal);
        dados.historiaDoencaAtual = valorCampo("id_historia_doenca_atual", dados.historiaDoencaAtual);
        dados.exameFisico = valorCampo("id_exame_fisico", dados.exameFisico);
        dados.hipoteseDiagnostica = valorCampo("id_hipotese_diagnostica", dados.hipoteseDiagnostica);
        dados.condutaCodigo = valorCampo("id_conduta", dados.condutaCodigo);
        dados.conduta = textoSelecionado("id_conduta", dados.conduta);
        dados.solicitaMedicacao = campoMarcado("id_solicita_medicacao", dados.solicitaMedicacao);
        dados.solicitaLaboratorio = campoMarcado("id_solicita_exames_laboratoriais", dados.solicitaLaboratorio);
        dados.solicitaImagem = campoMarcado("id_solicita_exames_imagem", dados.solicitaImagem);
        dados.examesLaboratoriais = valorCampo("id_exames_laboratoriais", dados.examesLaboratoriais);
        dados.examesImagem = valorCampo("id_exames_imagem", dados.examesImagem);
        dados.indicacaoRaiox = valorCampo("id_indicacao_raiox", dados.indicacaoRaiox);
        dados.indicacaoTomografia = valorCampo("id_indicacao_tomografia", dados.indicacaoTomografia);
        dados.indicacaoOutrosImagem = valorCampo("id_indicacao_outros_imagem", dados.indicacaoOutrosImagem);
        dados.prescricao = valorCampo("id_prescricao", dados.prescricao);
        dados.orientacoes = valorCampo("id_orientacoes", dados.orientacoes);
        dados.receita = valorCampo("id_receita", dados.receita);
        dados.atestado = valorCampo("id_atestado", dados.atestado);
        dados.atestadoDias = valorCampo("id_atestado_dias", dados.atestadoDias);
        dados.atestadoCid = valorCampo("id_atestado_cid", dados.atestadoCid);
        dados.atestadoCidDescricao = valorCampo("atestado_cid_descricao", dados.atestadoCidDescricao);
        dados.alergia = dados.alergia || "";
        dados.usoMedicamento = dados.usoMedicamento || "";
        dados.dataConsulta = dados.dataConsulta || new Date().toLocaleString("pt-BR");

        return dados;
    }

    function linha(label, valor, labelDois, valorDois) {
        return `
            <tr>
                <th>${escaparHtml(label)}</th>
                <td>${escaparHtml(textoOuTraco(valor))}</td>
                <th>${escaparHtml(labelDois)}</th>
                <td>${escaparHtml(textoOuTraco(valorDois))}</td>
            </tr>
        `;
    }

    function linhaTexto(label, valor) {
        return `
            <tr>
                <th>${escaparHtml(label)}</th>
                <td colspan="3">${textoLongo(valor)}</td>
            </tr>
        `;
    }

    function linhaProfissional(label, nome, labelRegistro, registro) {
        if (!temTexto(nome) && !temTexto(registro)) {
            return "";
        }

        return linha(label, nome, labelRegistro, registro);
    }

    function secao(titulo, conteudo) {
        return `
            <div class="secao">
                <div class="secao-titulo">${escaparHtml(titulo)}</div>
                ${conteudo}
            </div>
        `;
    }

    function tabela(conteudo) {
        return `<table>${conteudo}</table>`;
    }

    function cabecalhoDocumento(titulo, dados) {
        return `
            <div class="topo">
                <div>
                    <div class="setor">Sistema Hospitalar</div>
                    <h1>${escaparHtml(titulo)}</h1>
                </div>
                <div class="selo">${escaparHtml(textoOuTraco(dados.bam))}</div>
            </div>
            <div class="meta">
                <div><strong>Paciente</strong><span>${escaparHtml(textoOuTraco(dados.paciente))}</span></div>
                <div><strong>CPF</strong><span>${escaparHtml(textoOuTraco(dados.cpf))}</span></div>
                <div><strong>Idade</strong><span>${escaparHtml(textoOuTraco(dados.idade))} anos</span></div>
                <div><strong>Impressao</strong><span>${escaparHtml(new Date().toLocaleString("pt-BR"))}</span></div>
            </div>
        `;
    }

    function secaoPaciente(dados) {
        return secao("Identificacao", tabela(`
            ${linha("BAM", dados.bam, "Nascimento", dados.nascimento)}
            ${linha("Tipo", dados.tipo, "Status", dados.status)}
            ${linha("Chegada", dados.horaChegada, "Passagens", dados.passagens)}
        `));
    }

    function secaoAcolhimento(dados) {
        return secao("Sinais vitais do acolhimento", `
            <table class="vitals">
                <tr>
                    <th>PA</th>
                    <th>Temperatura</th>
                    <th>FR</th>
                    <th>Pulso</th>
                    <th>Dor</th>
                </tr>
                <tr>
                    <td>${escaparHtml(textoOuTraco(dados.pressao))}</td>
                    <td>${escaparHtml(textoOuTraco(dados.temperatura))} C</td>
                    <td>${escaparHtml(textoOuTraco(dados.fr))}</td>
                    <td>${escaparHtml(textoOuTraco(dados.pulso))} bpm</td>
                    <td>${escaparHtml(textoOuTraco(dados.dor))} / 10</td>
                </tr>
            </table>
        `);
    }

    function secaoClassificacao(dados) {
        if (
            !temTexto(dados.classificacao)
            && !temTexto(dados.queixaClassificacao)
            && !temTexto(dados.alergia)
            && !temTexto(dados.usoMedicamento)
        ) {
            return "";
        }

        return secao("Classificacao de risco", tabela(`
            ${linha("Classificacao", dados.classificacao, "Data", dados.dataClassificacao)}
            ${linhaTexto("Queixa", dados.queixaClassificacao)}
            ${linhaTexto("Alergia", dados.alergia)}
            ${linhaTexto("Uso de medicamento", dados.usoMedicamento)}
        `));
    }

    function secaoAlertaAlergia(dados) {
        if (!temTexto(dados.alergia)) {
            return "";
        }

        return `
            <div class="alerta-alergia">
                <strong>ATENCAO: PACIENTE COM ALERGIA REGISTRADA</strong>
                <div>${textoLongo(dados.alergia)}</div>
            </div>
        `;
    }

    function secaoConsulta(dados) {
        return secao("Consulta medica", tabela(`
            ${linha("Medico", dados.medicoResponsavel, "CRM", dados.crmMedico)}
            ${linha("Data", dados.dataConsulta, "CID", dados.cid)}
            ${linha("Conduta", dados.conduta, "Classificacao", dados.classificacao)}
            ${linhaTexto("Queixa principal", dados.queixaPrincipal)}
            ${linhaTexto("Historia da doenca atual", dados.historiaDoencaAtual)}
            ${linhaTexto("Exame fisico", dados.exameFisico)}
            ${linhaTexto("Hipotese diagnostica", dados.hipoteseDiagnostica)}
        `));
    }

    function secaoReavaliacoes(dados) {
        const reavaliacoes = Array.isArray(dados.reavaliacoes)
            ? dados.reavaliacoes
            : [];

        if (!reavaliacoes.length) {
            return "";
        }

        const linhas = reavaliacoes.map(function (reavaliacao) {
            return `
                ${linha("Medico", reavaliacao.medico, "CRM", reavaliacao.crm)}
                ${linha("Data", reavaliacao.data, "Conduta", reavaliacao.conduta)}
                ${linha("CID", reavaliacao.cid, "Registro", "Reavaliacao")}
                ${linhaTexto("Avaliacao", reavaliacao.avaliacao)}
                ${linhaTexto("Orientacoes", reavaliacao.orientacoes)}
            `;
        }).join("");

        return secao("Reavaliacoes medicas", tabela(linhas));
    }

    function secaoPedidoLaboratorio(dados) {
        return secao("Pedido de exames laboratoriais", tabela(`
            ${linha("Solicitado", dados.solicitaLaboratorio ? "Sim" : "Nao", "Data", dados.dataConsulta)}
            ${linha("Medico", dados.medicoResponsavel, "CRM", dados.crmMedico)}
            ${linhaTexto("Exames", dados.examesLaboratoriais)}
        `));
    }

    function secaoPedidoImagem(dados) {
        return secao("Pedido de exames de imagem", tabela(`
            ${linha("Solicitado", dados.solicitaImagem ? "Sim" : "Nao", "Data", dados.dataConsulta)}
            ${linha("Medico", dados.medicoResponsavel, "CRM", dados.crmMedico)}
            ${linhaTexto("Exames", dados.examesImagem)}
            ${linhaTexto("Indicacao Raio-X", dados.indicacaoRaiox)}
            ${linhaTexto("Indicacao Tomografia", dados.indicacaoTomografia)}
            ${linhaTexto("Indicacao outros exames", dados.indicacaoOutrosImagem)}
        `));
    }

    function secaoPrescricao(dados) {
        return secao("Prescricao / medicacao", tabela(`
            ${linha("Solicita medicacao", dados.solicitaMedicacao ? "Sim" : "Nao", "Data", dados.dataConsulta)}
            ${linha("Medico", dados.medicoResponsavel, "CRM", dados.crmMedico)}
            ${linhaTexto("Alergia registrada", dados.alergia)}
            ${linhaTexto("Prescricao", dados.prescricao)}
        `));
    }

    function secaoOrientacoes(dados) {
        return secao("Orientacoes e alta", tabela(`
            ${linha("Conduta", dados.conduta, "Data", dados.dataConsulta)}
            ${linhaTexto("Orientacoes", dados.orientacoes)}
        `));
    }

    function secaoReceita(dados) {
        return secao("Receita medica", tabela(`
            ${linha("Medico", dados.medicoResponsavel, "CRM", dados.crmMedico)}
            ${linhaTexto("Receita", dados.receita)}
        `));
    }

    function secaoAtestado(dados) {
        const dias = String(dados.atestadoDias || "").trim();
        const cid = String(dados.atestadoCid || "").trim();
        const textoAtestado = dias
            ? `Atesto, para os devidos fins, que o paciente necessita de ${dias} dia(s) de afastamento.`
            : textoOuTraco(dados.atestado);

        return secao("Atestado medico", tabela(`
            ${linha("Medico", dados.medicoResponsavel, "CRM", dados.crmMedico)}
            ${linha("Dias", dias || "-", "CID", cid || "Nao informado")}
            ${linhaTexto("Descricao do CID", dados.atestadoCidDescricao)}
            ${linhaTexto("Atestado", textoAtestado)}
        `));
    }

    function secaoResultados(dados) {
        const conteudo = `
            ${linhaTexto("Resultado laboratorio", dados.resultadoLaboratorio)}
            ${linha("Liberacao laboratorio", dados.dataResultadoLaboratorio, "Farmacia liberada", dados.farmaciaLiberada ? "Sim" : "Nao")}
            ${linhaProfissional("Tecnico laboratorio", dados.tecnicoLaboratorioNome, "Registro", dados.tecnicoLaboratorioRegistro)}
            ${linhaTexto("Resultado imagem", dados.resultadoImagem)}
            ${linha("Liberacao imagem", dados.dataResultadoImagem, "Conduta", dados.conduta)}
            ${linhaTexto("Resultado Raio-X", dados.resultadoRaiox)}
            ${linha("Liberacao Raio-X", dados.dataResultadoRaiox, "Liberacao Tomografia", dados.dataResultadoTomografia)}
            ${linhaProfissional("Tecnico Raio-X", dados.tecnicoRaioxNome, "Registro", dados.tecnicoRaioxRegistro)}
            ${linhaTexto("Laudo Tomografia", dados.resultadoTomografia)}
            ${linhaProfissional("Tecnico Tomografia", dados.tecnicoTomografiaNome, "Registro", dados.tecnicoTomografiaRegistro)}
            ${linhaTexto("Laudo Mamografia", dados.resultadoMamografia)}
            ${linha("Liberacao Mamografia", dados.dataResultadoMamografia, "Liberacao Densitometria", dados.dataResultadoDensitometria)}
            ${linhaProfissional("Tecnico Mamografia", dados.tecnicoMamografiaNome, "Registro", dados.tecnicoMamografiaRegistro)}
            ${linhaTexto("Laudo Densitometria", dados.resultadoDensitometria)}
            ${linhaProfissional("Tecnico Densitometria", dados.tecnicoDensitometriaNome, "Registro", dados.tecnicoDensitometriaRegistro)}
            ${linhaTexto("Medicamentos dispensados", dados.medicamentosDispensados)}
            ${linhaProfissional("Farmacia", dados.profissionalFarmaciaNome, "CRF/Registro", dados.profissionalFarmaciaRegistro)}
            ${linhaTexto("Medicacao administrada", dados.medicacaoAdministrada)}
            ${linhaProfissional("Enfermagem", dados.profissionalMedicacaoNome, "COREN", dados.profissionalMedicacaoRegistro)}
            ${linhaTexto("Observacoes da medicacao", dados.observacoesMedicacao)}
        `;

        return secao("Resultados e procedimentos", tabela(conteudo));
    }

    function assinatura(rotulo) {
        return `
            <div class="rodape">
                <div class="assinatura">${escaparHtml(rotulo || "Profissional responsavel")}</div>
                <div class="assinatura">Paciente / responsavel</div>
            </div>
        `;
    }

    function montarDocumento(titulo, dados, secoes, rotuloAssinatura) {
        return `
            <article class="documento">
                ${cabecalhoDocumento(titulo, dados)}
                ${secaoPaciente(dados)}
                ${secaoAlertaAlergia(dados)}
                ${secoes.join("")}
                ${assinatura(rotuloAssinatura)}
            </article>
        `;
    }

    function documentoPorTipo(tipo, dados) {
        if (tipo === "laboratorio") {
            return montarDocumento(
                "Pedido de Exames Laboratoriais",
                dados,
                [secaoPedidoLaboratorio(dados)],
                "Medico solicitante"
            );
        }

        if (tipo === "imagem") {
            return montarDocumento(
                "Pedido de Exames de Imagem",
                dados,
                [secaoPedidoImagem(dados)],
                "Medico solicitante"
            );
        }

        if (tipo === "prescricao") {
            return montarDocumento(
                "Prescricao Medica",
                dados,
                [secaoPrescricao(dados)],
                "Medico responsavel"
            );
        }

        if (tipo === "orientacoes") {
            return montarDocumento(
                "Orientacoes / Alta Medica",
                dados,
                [secaoOrientacoes(dados)],
                "Medico responsavel"
            );
        }

        if (tipo === "receita") {
            return montarDocumento(
                "Receita Medica",
                dados,
                [secaoReceita(dados)],
                "Medico responsavel"
            );
        }

        if (tipo === "atestado") {
            return montarDocumento(
                "Atestado Medico",
                dados,
                [secaoAtestado(dados)],
                "Medico responsavel"
            );
        }

        if (tipo === "resultados") {
            return montarDocumento(
                "Resumo de Alta e Resultados",
                dados,
                [secaoConsulta(dados), secaoReavaliacoes(dados), secaoResultados(dados), secaoOrientacoes(dados)],
                "Medico responsavel"
            );
        }

        return montarDocumento(
            "Ficha de Consulta Medica",
            dados,
            [secaoAcolhimento(dados), secaoClassificacao(dados), secaoConsulta(dados), secaoReavaliacoes(dados)],
            "Medico responsavel"
        );
    }

    function tiposParaImprimirTudo(dados) {
        const tipos = ["consulta"];

        if (dados.solicitaLaboratorio || temTexto(dados.examesLaboratoriais)) {
            tipos.push("laboratorio");
        }

        if (dados.solicitaImagem || temTexto(dados.examesImagem)) {
            tipos.push("imagem");
        }

        if (dados.solicitaMedicacao || temTexto(dados.prescricao)) {
            tipos.push("prescricao");
        }

        if (temTexto(dados.receita)) {
            tipos.push("receita");
        }

        if (temTexto(dados.atestadoDias) || temTexto(dados.atestadoCid) || temTexto(dados.atestado)) {
            tipos.push("atestado");
        }

        if (
            temTexto(dados.resultadoLaboratorio) ||
            temTexto(dados.resultadoImagem) ||
            temTexto(dados.resultadoRaiox) ||
            temTexto(dados.resultadoTomografia) ||
            temTexto(dados.resultadoMamografia) ||
            temTexto(dados.resultadoDensitometria) ||
            temTexto(dados.medicamentosDispensados) ||
            temTexto(dados.medicacaoAdministrada) ||
            dados.condutaCodigo === "ALTA" ||
            (Array.isArray(dados.reavaliacoes) && dados.reavaliacoes.length > 0)
        ) {
            tipos.push("resultados");
        } else if (temTexto(dados.orientacoes)) {
            tipos.push("orientacoes");
        }

        return tipos;
    }

    function montarPagina(titulo, documentos) {
        return `
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <title>${escaparHtml(titulo)}</title>
                <style>
                    * { box-sizing: border-box; }
                    @page { margin: 10mm; size: A4; }
                    body {
                        background: #fff;
                        color: #0f172a;
                        font-family: Arial, Helvetica, sans-serif;
                        font-size: 12px;
                        margin: 0;
                    }
                    .documento {
                        border: 1px solid #cbd5e1;
                        margin: 0 auto 16px;
                        max-width: 780px;
                    }
                    .documento:not(:last-child) {
                        page-break-after: always;
                    }
                    .topo {
                        align-items: center;
                        background: #0f4c81;
                        color: #fff;
                        display: flex;
                        justify-content: space-between;
                        padding: 12px 14px;
                    }
                    .setor {
                        font-size: 11px;
                        font-weight: 700;
                        text-transform: uppercase;
                    }
                    h1 {
                        font-size: 18px;
                        line-height: 1.1;
                        margin: 4px 0 0;
                    }
                    .selo {
                        border: 1px solid rgba(255, 255, 255, .55);
                        border-radius: 999px;
                        font-size: 13px;
                        font-weight: 900;
                        padding: 8px 12px;
                    }
                    .meta {
                        border-bottom: 1px solid #cbd5e1;
                        display: grid;
                        grid-template-columns: 2fr 1fr 1fr 1fr;
                    }
                    .meta div {
                        border-right: 1px solid #cbd5e1;
                        padding: 7px 10px;
                    }
                    .meta div:last-child {
                        border-right: 0;
                    }
                    .meta strong {
                        color: #475569;
                        display: block;
                        font-size: 10px;
                        text-transform: uppercase;
                    }
                    .meta span {
                        display: block;
                        font-weight: 800;
                        margin-top: 3px;
                    }
                    .secao {
                        padding: 12px 14px 0;
                    }
                    .alerta-alergia {
                        background: #fee2e2;
                        border: 2px solid #dc2626;
                        color: #7f1d1d;
                        font-size: 13px;
                        font-weight: 800;
                        margin: 12px 14px 0;
                        padding: 10px 12px;
                    }
                    .alerta-alergia strong {
                        display: block;
                        margin-bottom: 4px;
                    }
                    .secao-titulo {
                        border-bottom: 2px solid #0f4c81;
                        color: #0f4c81;
                        font-size: 13px;
                        font-weight: 900;
                        margin-bottom: 8px;
                        padding-bottom: 4px;
                        text-transform: uppercase;
                    }
                    table {
                        border-collapse: collapse;
                        margin-bottom: 10px;
                        width: 100%;
                    }
                    th, td {
                        border: 1px solid #cbd5e1;
                        padding: 7px 8px;
                        text-align: left;
                        vertical-align: top;
                    }
                    th {
                        background: #f1f5f9;
                        color: #334155;
                        font-size: 10px;
                        text-transform: uppercase;
                        width: 20%;
                    }
                    .vitals th,
                    .vitals td {
                        text-align: center;
                        width: auto;
                    }
                    .vitals td {
                        font-weight: 900;
                    }
                    .rodape {
                        display: grid;
                        gap: 22px;
                        grid-template-columns: 1fr 1fr;
                        padding: 24px 14px 14px;
                    }
                    .assinatura {
                        border-top: 1px solid #0f172a;
                        padding-top: 6px;
                        text-align: center;
                    }
                    .print-actions {
                        margin: 12px auto 0;
                        max-width: 780px;
                        text-align: right;
                    }
                    .print-actions button {
                        background: #0f4c81;
                        border: 0;
                        border-radius: 6px;
                        color: #fff;
                        cursor: pointer;
                        font-weight: 800;
                        padding: 9px 14px;
                    }
                    @media print {
                        body {
                            -webkit-print-color-adjust: exact;
                            print-color-adjust: exact;
                        }
                        .documento {
                            border-color: #111827;
                            max-width: none;
                        }
                        .print-actions {
                            display: none;
                        }
                    }
                </style>
            </head>
            <body>
                ${documentos}
                <div class="print-actions">
                    <button type="button" onclick="window.print()">Imprimir</button>
                </div>
            </body>
            </html>
        `;
    }

    function abrirImpressao(titulo, documentos) {
        const janela = window.open("", "_blank", "width=840,height=900");

        if (!janela) {
            alert("O navegador bloqueou a janela de impressao. Libere pop-ups para imprimir.");
            return;
        }

        janela.document.open();
        janela.document.write(montarPagina(titulo, documentos));
        janela.document.close();
        janela.focus();

        setTimeout(function () {
            janela.print();
        }, 300);
    }

    function imprimir(tipo, dados) {
        abrirImpressao("Impressao Medica", documentoPorTipo(tipo, dados || {}));
    }

    function imprimirTudo(dados) {
        const ficha = dados || {};
        const documentos = tiposParaImprimirTudo(ficha)
            .map(function (tipo) {
                return documentoPorTipo(tipo, ficha);
            })
            .join("");

        abrirImpressao("Documentos da Consulta Medica", documentos);
    }

    window.MedicoImpressao = {
        coletarFormulario: coletarFormulario,
        imprimir: imprimir,
        imprimirTudo: imprimirTudo,
        lerJson: lerJson,
    };
})();
