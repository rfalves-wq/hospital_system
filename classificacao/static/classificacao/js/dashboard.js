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

function obterDadosImpressaoClassificacao() {
    const script = document.getElementById("dados-impressao-classificacao");

    if (!script) {
        return null;
    }

    try {
        return JSON.parse(script.textContent);
    } catch (erro) {
        return null;
    }
}

function classeClassificacao(texto) {
    const valor = String(texto || "").toLowerCase();

    if (valor.includes("vermelho")) return "vermelho";
    if (valor.includes("laranja")) return "laranja";
    if (valor.includes("amarelo")) return "amarelo";
    if (valor.includes("verde")) return "verde";
    if (valor.includes("azul")) return "azul";

    return "neutro";
}

function montarLinha(label, valor, labelDois, valorDois) {
    return `
        <tr>
            <th>${escaparHtml(label)}</th>
            <td>${escaparHtml(textoOuTraco(valor))}</td>
            <th>${escaparHtml(labelDois)}</th>
            <td>${escaparHtml(textoOuTraco(valorDois))}</td>
        </tr>
    `;
}

function imprimirFichaPacienteClassificacao(dados) {
    const ficha = dados || {};
    const agora = new Date();
    const classificacao = ficha.classificacao || "";
    const classificacaoClasse = classeClassificacao(classificacao);
    const pesoAltura = (ficha.peso || ficha.altura)
        ? `${textoOuTraco(ficha.peso)} kg / ${textoOuTraco(ficha.altura)} m`
        : "";

    const blocoClassificacao = classificacao ? `
        <div class="secao">
            <div class="secao-titulo">Classificacao de risco</div>
            <table>
                ${montarLinha("Classificacao", classificacao, "Hora", ficha.horaClassificacao)}
                ${montarLinha("Responsavel", ficha.responsavel, "COREN / registro", ficha.responsavelRegistro)}
                ${montarLinha("Forma chegada", ficha.formaChegada, "Tempo sintoma", ficha.tempoSintoma)}
                ${montarLinha("Escala dor", ficha.escalaDor, "Possivel gravidez", ficha.possivelGravidez)}
                ${montarLinha("Deficiencia", ficha.deficiencia, "Glicemia", ficha.glicemia)}
                ${montarLinha("Peso / altura", pesoAltura, "Chamadas", ficha.chamadas)}
                <tr>
                    <th>Queixa</th>
                    <td colspan="3">${escaparHtml(textoOuTraco(ficha.queixa))}</td>
                </tr>
                <tr>
                    <th>Doenca pre-existente</th>
                    <td colspan="3">${escaparHtml(textoOuTraco(ficha.doencaPreExistente))}</td>
                </tr>
                <tr>
                    <th>Alergia</th>
                    <td colspan="3">${escaparHtml(textoOuTraco(ficha.alergia))}</td>
                </tr>
                <tr>
                    <th>Uso de medicamento</th>
                    <td colspan="3">${escaparHtml(textoOuTraco(ficha.usoMedicamento))}</td>
                </tr>
                <tr>
                    <th>Observacoes</th>
                    <td colspan="3">${escaparHtml(textoOuTraco(ficha.observacoes))}</td>
                </tr>
            </table>
        </div>
    ` : "";

    const conteudo = `
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <title>Ficha do Paciente - Classificacao</title>
            <style>
                * {
                    box-sizing: border-box;
                }

                @page {
                    margin: 10mm;
                    size: A4;
                }

                body {
                    background: #fff;
                    color: #0f172a;
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 12px;
                    margin: 0;
                }

                .folha {
                    border: 1px solid #cbd5e1;
                    margin: 0 auto;
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
                    letter-spacing: .08em;
                    text-transform: uppercase;
                }

                h1 {
                    font-size: 18px;
                    line-height: 1.1;
                    margin: 4px 0 0;
                }

                .badge {
                    border-radius: 999px;
                    color: #fff;
                    font-size: 12px;
                    font-weight: 900;
                    min-width: 130px;
                    padding: 8px 12px;
                    text-align: center;
                }

                .badge.vermelho {
                    background: #dc3545;
                }

                .badge.laranja {
                    background: #f97316;
                }

                .badge.amarelo {
                    background: #f59e0b;
                    color: #111827;
                }

                .badge.verde {
                    background: #198754;
                }

                .badge.azul {
                    background: #0d6efd;
                }

                .badge.neutro {
                    background: #64748b;
                }

                .meta {
                    border-bottom: 1px solid #cbd5e1;
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                }

                .meta div {
                    border-right: 1px solid #cbd5e1;
                    padding: 7px 10px;
                }

                .meta div:last-child {
                    border-right: 0;
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

                th,
                td {
                    border: 1px solid #cbd5e1;
                    padding: 7px 8px;
                    text-align: left;
                    vertical-align: top;
                }

                th {
                    background: #f1f5f9;
                    color: #334155;
                    font-size: 10px;
                    letter-spacing: .04em;
                    text-transform: uppercase;
                    width: 20%;
                }

                .valor-forte {
                    font-size: 14px;
                    font-weight: 900;
                    text-transform: uppercase;
                }

                .vitals th {
                    text-align: center;
                    width: auto;
                }

                .vitals td {
                    font-size: 13px;
                    font-weight: 900;
                    text-align: center;
                }

                .observacao {
                    background: #f8fafc;
                    border: 1px solid #cbd5e1;
                    color: #475569;
                    font-size: 11px;
                    line-height: 1.4;
                    margin-bottom: 12px;
                    padding: 8px;
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
                    .print-actions {
                        display: none;
                    }

                    .folha {
                        border-color: #111827;
                        max-width: none;
                    }

                    body {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                }
            </style>
        </head>
        <body>
            <div class="folha">
                <div class="topo">
                    <div>
                        <div class="setor">Classificacao de Risco</div>
                        <h1>Ficha de Dados do Paciente</h1>
                    </div>

                    <div class="badge ${escaparHtml(classificacaoClasse)}">
                        ${escaparHtml(textoOuTraco(classificacao || ficha.status))}
                    </div>
                </div>

                <div class="meta">
                    <div>
                        <strong>BAM</strong><br>
                        <span>${escaparHtml(textoOuTraco(ficha.bam))}</span>
                    </div>
                    <div>
                        <strong>Chegada</strong><br>
                        <span>${escaparHtml(textoOuTraco(ficha.horaChegada))}</span>
                    </div>
                    <div>
                        <strong>Passagens</strong><br>
                        <span>${escaparHtml(textoOuTraco(ficha.passagens))}</span>
                    </div>
                    <div>
                        <strong>Impressao</strong><br>
                        <span>${escaparHtml(agora.toLocaleString("pt-BR"))}</span>
                    </div>
                </div>

                <div class="secao">
                    <div class="secao-titulo">Paciente</div>
                    <table>
                        <tr>
                            <th>Nome</th>
                            <td colspan="3" class="valor-forte">${escaparHtml(textoOuTraco(ficha.paciente))}</td>
                        </tr>
                        ${montarLinha("CPF", ficha.cpf, "Nascimento", ficha.nascimento)}
                        ${montarLinha("Idade", `${textoOuTraco(ficha.idade)} anos`, "Tipo", ficha.tipo)}
                        ${montarLinha("Data acolhimento", ficha.dataAcolhimento, "Status", ficha.status)}
                    </table>
                </div>

                <div class="secao">
                    <div class="secao-titulo">Sinais vitais do acolhimento</div>
                    <table class="vitals">
                        <tr>
                            <th>PA</th>
                            <th>Temperatura</th>
                            <th>FR</th>
                            <th>Pulso</th>
                            <th>Dor</th>
                            <th>Chamadas</th>
                        </tr>
                        <tr>
                            <td>${escaparHtml(textoOuTraco(ficha.pressao))}</td>
                            <td>${escaparHtml(textoOuTraco(ficha.temperatura))} C</td>
                            <td>${escaparHtml(textoOuTraco(ficha.fr))}</td>
                            <td>${escaparHtml(textoOuTraco(ficha.pulso))} bpm</td>
                            <td>${escaparHtml(textoOuTraco(ficha.dor))} / 10</td>
                            <td>${escaparHtml(textoOuTraco(ficha.chamadas))}</td>
                        </tr>
                    </table>

                    <div class="observacao">
                        Esta ficha reune os dados do paciente para apoio ao fluxo da classificacao de risco.
                    </div>
                </div>

                ${blocoClassificacao}

                <div class="rodape">
                    <div class="assinatura">Profissional da classificacao</div>
                    <div class="assinatura">Paciente / responsavel</div>
                </div>
            </div>

            <div class="print-actions">
                <button type="button" onclick="window.print()">Imprimir ficha</button>
            </div>
        </body>
        </html>
    `;

    const janela = window.open("", "_blank", "width=840,height=900");

    if (!janela) {
        alert("O navegador bloqueou a janela de impressao. Libere pop-ups para imprimir a ficha.");
        return;
    }

    janela.document.open();
    janela.document.write(conteudo);
    janela.document.close();
    janela.focus();

    setTimeout(function () {
        janela.print();
    }, 300);
}

document.addEventListener("DOMContentLoaded", function () {
    const dadosImpressao = obterDadosImpressaoClassificacao();
    const botaoImprimir = document.getElementById("btn-imprimir-classificacao");
    const modalElemento = document.getElementById("modal-impressao-classificacao");

    if (modalElemento && window.bootstrap) {
        const modal = new bootstrap.Modal(modalElemento);
        modal.show();

        modalElemento.addEventListener("hidden.bs.modal", function () {
            const script = document.getElementById("dados-impressao-classificacao");

            if (script) {
                script.remove();
            }
        });
    }

    if (botaoImprimir && dadosImpressao) {
        botaoImprimir.addEventListener("click", function () {
            imprimirFichaPacienteClassificacao(dadosImpressao);

            if (modalElemento && window.bootstrap) {
                bootstrap.Modal.getOrCreateInstance(modalElemento).hide();
            }
        });
    }
});
