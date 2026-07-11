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

    function textoLongo(valor) {
        return escaparHtml(textoOuTraco(valor)).replace(/\r?\n/g, "<br>");
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

    function cabecalho(titulo, dados) {
        return `
            <div class="topo">
                <div>
                    <div class="setor">Centro de Internacoes</div>
                    <h1>${escaparHtml(titulo)}</h1>
                </div>
                <div class="selo">Leito ${escaparHtml(textoOuTraco(dados.leito))}</div>
            </div>
            <div class="meta">
                <div><strong>Paciente</strong><span>${escaparHtml(textoOuTraco(dados.paciente))}</span></div>
                <div><strong>BAM</strong><span>${escaparHtml(textoOuTraco(dados.bam))}</span></div>
                <div><strong>Idade</strong><span>${escaparHtml(textoOuTraco(dados.idade))} anos</span></div>
                <div><strong>Impressao</strong><span>${escaparHtml(new Date().toLocaleString("pt-BR"))}</span></div>
            </div>
        `;
    }

    function secaoIdentificacao(dados) {
        return secao("Identificacao do paciente", tabela(`
            ${linha("CPF", dados.cpf, "Nascimento", dados.nascimento)}
            ${linha("Tipo", dados.tipoAtendimento, "Status", dados.statusPaciente)}
            ${linha("Chegada", dados.horaChegada, "Classificacao", dados.classificacao)}
            ${linhaTexto("Queixa da classificacao", dados.queixaClassificacao)}
        `));
    }

    function secaoDadosInternacao(dados) {
        return secao("Dados da internacao", tabela(`
            ${linha("Leito", dados.leito, "Setor", dados.setor)}
            ${linha("Admissao", dados.dataInternacao, "Status", dados.statusInternacao)}
            ${linha("Medico", dados.medico, "CRM", dados.crm)}
            ${linha("CID", dados.cid, "Responsavel", dados.profissionalResponsavel)}
            ${linhaTexto("Diagnostico / motivo", dados.diagnosticoAdmissao || dados.hipotese)}
            ${linhaTexto("Cuidados iniciais", dados.cuidados)}
            ${linhaTexto("Orientacoes medicas", dados.orientacoesMedicas)}
            ${linhaTexto("Observacoes", dados.observacoes)}
        `));
    }

    function secaoEvolucao(evolucao) {
        const item = evolucao || {};

        return secao("Evolucao da internacao", tabela(`
            ${linha("Data", item.data, "Profissional", item.profissional)}
            ${linha("PA", item.pressao, "Temperatura", item.temperatura ? `${item.temperatura} C` : "")}
            ${linha("Pulso", item.pulso ? `${item.pulso} bpm` : "", "FR", item.fr)}
            ${linha("Saturacao", item.saturacao ? `${item.saturacao}%` : "", "Leito", "")}
            ${linhaTexto("Evolucao", item.evolucao)}
            ${linhaTexto("Conduta", item.conduta)}
        `));
    }

    function secaoEvolucoes(dados) {
        const evolucoes = dados.evolucoes || [];

        if (evolucoes.length === 0) {
            return secao("Evolucoes", "<div class=\"observacao\">Nenhuma evolucao registrada.</div>");
        }

        return evolucoes.map(secaoEvolucao).join("");
    }

    function secaoAlta(dados) {
        return secao("Alta da internacao", tabela(`
            ${linha("Data da alta", dados.dataAlta, "Profissional", dados.profissionalAlta)}
            ${linhaTexto("Resumo da alta", dados.resumoAlta)}
        `));
    }

    function assinatura(rotulo) {
        return `
            <div class="rodape">
                <div class="assinatura">${escaparHtml(rotulo || "Profissional responsavel")}</div>
                <div class="assinatura">Paciente / responsavel</div>
            </div>
        `;
    }

    function montarDocumento(titulo, dados, secoes, assinaturaTexto) {
        return `
            <article class="documento">
                ${cabecalho(titulo, dados)}
                ${secaoIdentificacao(dados)}
                ${secoes.join("")}
                ${assinatura(assinaturaTexto)}
            </article>
        `;
    }

    function documentoPorTipo(tipo, dados) {
        if (tipo === "evolucao") {
            return montarDocumento(
                "Evolucao da Internacao",
                dados,
                [secaoDadosInternacao(dados), secaoEvolucao(dados.evolucaoImpressao)],
                "Profissional da evolucao"
            );
        }

        if (tipo === "alta") {
            return montarDocumento(
                "Alta da Internacao",
                dados,
                [secaoDadosInternacao(dados), secaoEvolucoes(dados), secaoAlta(dados)],
                "Profissional responsavel pela alta"
            );
        }

        if (tipo === "completo") {
            const secoes = [secaoDadosInternacao(dados), secaoEvolucoes(dados)];

            if (dados.dataAlta || dados.resumoAlta) {
                secoes.push(secaoAlta(dados));
            }

            return montarDocumento(
                "Ficha Completa da Internacao",
                dados,
                secoes,
                "Profissional responsavel"
            );
        }

        return montarDocumento(
            "Admissao da Internacao",
            dados,
            [secaoDadosInternacao(dados)],
            "Profissional responsavel pela admissao"
        );
    }

    function montarPagina(titulo, documento) {
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
                    .observacao {
                        background: #f8fafc;
                        border: 1px solid #cbd5e1;
                        color: #475569;
                        padding: 10px;
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
                ${documento}
                <div class="print-actions">
                    <button type="button" onclick="window.print()">Imprimir</button>
                </div>
            </body>
            </html>
        `;
    }

    function imprimir(tipo, dados) {
        const ficha = dados || {};
        const documento = documentoPorTipo(tipo || ficha.tipoImpressao || "admissao", ficha);
        const janela = window.open("", "_blank", "width=840,height=900");

        if (!janela) {
            alert("O navegador bloqueou a janela de impressao. Libere pop-ups para imprimir.");
            return;
        }

        janela.document.open();
        janela.document.write(montarPagina("Internacao", documento));
        janela.document.close();
        janela.focus();

        setTimeout(function () {
            janela.print();
        }, 300);
    }

    window.InternacaoImpressao = {
        imprimir: imprimir,
        lerJson: lerJson,
    };
})();
