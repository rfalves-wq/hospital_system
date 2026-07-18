document.addEventListener("DOMContentLoaded", function () {
    // =========================
    // MÁSCARA CPF
    // =========================
    const cpf = document.getElementById("cpf");

    if (cpf) {
        cpf.addEventListener("input", function (e) {
            let v = e.target.value.replace(/\D/g, "");

            v = v.slice(0, 11);
            v = v.replace(/(\d{3})(\d)/, "$1.$2");
            v = v.replace(/(\d{3})(\d)/, "$1.$2");
            v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

            e.target.value = v;
        });
    }

    // =========================
    // CALCULAR IDADE
    // =========================
    const dataNascimento = document.getElementById("data_nascimento");
    const idade = document.getElementById("idade");

    function calcularIdade(data) {
        const nasc = new Date(data);
        const hoje = new Date();

        let anos = hoje.getFullYear() - nasc.getFullYear();
        const mes = hoje.getMonth() - nasc.getMonth();

        if (
            mes < 0 ||
            (mes === 0 && hoje.getDate() < nasc.getDate())
        ) {
            anos--;
        }

        return anos;
    }

    function atualizarIdade() {
        if (!dataNascimento || !idade) {
            return;
        }

        if (!dataNascimento.value) {
            idade.value = "";
            return;
        }

        idade.value = calcularIdade(dataNascimento.value);
    }

    if (dataNascimento && idade) {
        dataNascimento.addEventListener("change", atualizarIdade);
        dataNascimento.addEventListener("input", atualizarIdade);
    }

    // =========================
    // BUSCA AUTOMÁTICA
    // =========================
    const horaChegada = document.getElementById("hora_chegada");

    if (horaChegada && !horaChegada.value) {
        const agora = new Date();
        const horas = String(agora.getHours()).padStart(2, "0");
        const minutos = String(agora.getMinutes()).padStart(2, "0");

        horaChegada.value = `${horas}:${minutos}`;
    }

    const busca = document.getElementById("busca");
    const tabela = document.getElementById("resultado-busca");
    const tabelaPacientes = document.getElementById("tabela-pacientes");
    const alertaPassagensDia = document.getElementById("alerta-passagens-dia");

    function escaparHtml(valor) {
        return String(valor || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function textoLimpo(valor) {
        if (valor === undefined || valor === null) {
            return "";
        }

        return String(valor).trim();
    }

    function textoOuTraco(valor) {
        const texto = textoLimpo(valor);

        return texto || "-";
    }

    function conselhoRegistroTexto(conselho, registro) {
        const conselhoLimpo = textoLimpo(conselho);
        const registroLimpo = textoLimpo(registro);

        if (conselhoLimpo && registroLimpo) {
            return `${conselhoLimpo} ${registroLimpo}`;
        }

        return conselhoLimpo || registroLimpo || "-";
    }

    function nomeTipoAtendimento(tipo) {
        const tipos = {
            NORMAL: "Atendimento Normal",
            RISCO: "Classificacao de Risco",
            PREFERENCIAL: "Atendimento Preferencial"
        };

        return tipos[tipo] || tipo || "-";
    }

    function classeTipoAtendimento(tipo) {
        return {
            NORMAL: "normal",
            RISCO: "risco",
            PREFERENCIAL: "preferencial"
        }[tipo] || "normal";
    }

    function normalizarDadosImpressao(dados) {
        const ficha = dados || {};
        const tipoAtendimento = ficha.tipo_atendimento || ficha.tipoAtendimento || "";
        const profissionalConselho = (
            ficha.profissional_conselho ||
            ficha.profissionalConselho ||
            (window.SistemaHospitalar && window.SistemaHospitalar.profissionalLogadoConselho)
        );
        const profissionalRegistro = (
            ficha.profissional_registro ||
            ficha.profissionalRegistro ||
            (window.SistemaHospitalar && window.SistemaHospitalar.profissionalLogadoRegistro)
        );
        const profissionalConselhoRegistro = (
            ficha.profissional_conselho_registro ||
            ficha.profissionalConselhoRegistro ||
            (window.SistemaHospitalar && window.SistemaHospitalar.profissionalLogadoConselhoRegistro) ||
            conselhoRegistroTexto(profissionalConselho, profissionalRegistro)
        );

        return {
            nomePaciente: textoOuTraco(ficha.nome_paciente || ficha.nomePaciente),
            cpfPaciente: textoOuTraco(ficha.cpf || ficha.cpfPaciente),
            dataNascimentoPaciente: textoOuTraco(ficha.data_nascimento || ficha.dataNascimentoPaciente),
            idadePaciente: textoOuTraco(ficha.idade || ficha.idadePaciente),
            horaChegadaPaciente: textoOuTraco(ficha.hora_chegada || ficha.horaChegadaPaciente),
            pressao: textoOuTraco(ficha.pressao_arterial || ficha.pressao),
            temperatura: textoOuTraco(ficha.temperatura),
            frequencia: textoOuTraco(ficha.frequencia_respiratoria || ficha.frequencia),
            pulso: textoOuTraco(ficha.pulso),
            dor: textoOuTraco(ficha.dor),
            tipoAtendimento: tipoAtendimento,
            tipoTexto: textoOuTraco(
                ficha.tipo_atendimento_label ||
                ficha.tipoTexto ||
                nomeTipoAtendimento(tipoAtendimento)
            ),
            numeroBam: textoOuTraco(ficha.numero_bam || ficha.numeroBam),
            dataAcolhimento: textoOuTraco(ficha.data_acolhimento || ficha.dataAcolhimento),
            profissionalResponsavel: textoOuTraco(
                ficha.profissional_responsavel ||
                ficha.profissionalResponsavel ||
                (window.SistemaHospitalar && window.SistemaHospitalar.profissionalLogado)
            ),
            profissionalConselho: textoOuTraco(profissionalConselho),
            profissionalRegistro: textoOuTraco(profissionalRegistro),
            profissionalConselhoRegistro: textoOuTraco(profissionalConselhoRegistro)
        };
    }

    function obterDadosImpressaoSalva() {
        const script = document.getElementById("dados-impressao-acolhimento");

        if (!script) {
            return null;
        }

        try {
            return JSON.parse(script.textContent);
        } catch (erro) {
            return null;
        }
    }

    function imprimirDadosPaciente(dados) {
        const agora = new Date();
        const ficha = normalizarDadosImpressao(dados);
        const tipoClasse = classeTipoAtendimento(ficha.tipoAtendimento);

        const conteudo = `
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <title>Comprovante de Acolhimento</title>
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
                        max-width: 760px;
                    }

                    .topo {
                        align-items: center;
                        background: #0f4c81;
                        color: #fff;
                        display: flex;
                        justify-content: space-between;
                        padding: 12px 14px;
                    }

                    .hospital {
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

                    .tipo {
                        border-radius: 999px;
                        color: #111827;
                        font-size: 13px;
                        font-weight: 900;
                        padding: 8px 12px;
                        text-align: center;
                        white-space: nowrap;
                    }

                    .tipo.normal {
                        background: #facc15;
                    }

                    .tipo.risco {
                        background: #dc3545;
                        color: #fff;
                    }

                    .tipo.preferencial {
                        background: #198754;
                        color: #fff;
                    }

                    .meta {
                        border-bottom: 1px solid #cbd5e1;
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
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
                        width: 22%;
                    }

                    .vitals th {
                        text-align: center;
                        width: auto;
                    }

                    .vitals td {
                        font-size: 14px;
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
                        display: block;
                        padding: 22px 14px 14px;
                    }

                    .assinatura {
                        border-top: 1px solid #0f172a;
                        padding-top: 6px;
                        text-align: center;
                    }

                    .print-actions {
                        margin: 12px auto 0;
                        max-width: 760px;
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

                    .muted {
                        color: #64748b;
                        font-size: 11px;
                    }

                    .valor-forte {
                        font-size: 14px;
                        font-weight: 900;
                        text-transform: uppercase;
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
                            <div class="hospital">Recepcao e Acolhimento</div>
                            <h1>Comprovante de Atendimento</h1>
                        </div>

                        <div class="tipo ${escaparHtml(tipoClasse)}">${escaparHtml(ficha.tipoTexto)}</div>
                    </div>

                    <div class="meta">
                        <div>
                            <strong>Data/Hora da impressao</strong><br>
                            <span>${escaparHtml(agora.toLocaleString("pt-BR"))}</span>
                        </div>

                        <div>
                            <strong>Hora da chegada</strong><br>
                            <span>${escaparHtml(ficha.horaChegadaPaciente)}</span>
                        </div>

                        <div>
                            <strong>Registro</strong><br>
                            <span>${escaparHtml(ficha.numeroBam)}</span>
                        </div>
                    </div>

                    <div class="secao">
                        <div class="secao-titulo">Dados do paciente</div>

                        <table>
                            <tr>
                                <th>Paciente</th>
                                <td colspan="3" class="valor-forte">${escaparHtml(ficha.nomePaciente)}</td>
                            </tr>
                            <tr>
                                <th>BAM</th>
                                <td>${escaparHtml(ficha.numeroBam)}</td>
                                <th>Acolhimento</th>
                                <td>${escaparHtml(ficha.dataAcolhimento)}</td>
                            </tr>
                            <tr>
                                <th>CPF</th>
                                <td>${escaparHtml(ficha.cpfPaciente)}</td>
                                <th>Nascimento</th>
                                <td>${escaparHtml(ficha.dataNascimentoPaciente)}</td>
                            </tr>
                            <tr>
                                <th>Idade</th>
                                <td>${escaparHtml(ficha.idadePaciente)} anos</td>
                                <th>Tipo</th>
                                <td>${escaparHtml(ficha.tipoTexto)}</td>
                            </tr>
                            <tr>
                                <th>Profissional</th>
                                <td>${escaparHtml(ficha.profissionalResponsavel)}</td>
                                <th>Conselho regional</th>
                                <td>${escaparHtml(ficha.profissionalConselhoRegistro)}</td>
                            </tr>
                        </table>
                    </div>

                    <div class="secao">
                        <div class="secao-titulo">Sinais vitais</div>

                        <table class="vitals">
                            <tr>
                                <th>Pressao arterial</th>
                                <th>Temperatura</th>
                                <th>Freq. respiratoria</th>
                                <th>Pulso</th>
                                <th>Dor</th>
                            </tr>
                            <tr>
                                <td>${escaparHtml(ficha.pressao)}</td>
                                <td>${escaparHtml(ficha.temperatura)} C</td>
                                <td>${escaparHtml(ficha.frequencia)}</td>
                                <td>${escaparHtml(ficha.pulso)}</td>
                                <td>${escaparHtml(ficha.dor)} / 10</td>
                            </tr>
                        </table>

                        <div class="observacao">
                            Esta ficha acompanha o paciente para continuidade do fluxo de atendimento.
                            Confira os dados antes de encaminhar.
                        </div>
                    </div>

                    <div class="rodape">
                        <div class="assinatura">
                            ${escaparHtml(ficha.profissionalResponsavel)}<br>
                            Conselho regional: ${escaparHtml(ficha.profissionalConselhoRegistro)}<br>
                            Responsavel pelo acolhimento
                        </div>
                    </div>
                </div>

                <div class="print-actions">
                    <button type="button" onclick="window.print()">Imprimir ficha</button>
                </div>
            </body>
            </html>
        `;

        const janela = window.open("", "_blank", "width=820,height=900");

        if (!janela) {
            alert("O navegador bloqueou a janela de impressao. Libere pop-ups para imprimir a ficha.");
            return false;
        }

        janela.document.open();
        janela.document.write(conteudo);
        janela.document.close();
        janela.focus();

        setTimeout(function () {
            janela.print();
        }, 300);

        return true;
    }

    function dadosReimpressaoDoBotao(botao) {
        const dados = botao.dataset;

        return {
            nome_paciente: dados.nomePaciente,
            cpf: dados.cpf,
            numero_bam: dados.numeroBam,
            data_nascimento: dados.dataNascimento,
            idade: dados.idade,
            hora_chegada: dados.horaChegada,
            pressao_arterial: dados.pressaoArterial,
            temperatura: dados.temperatura,
            frequencia_respiratoria: dados.frequenciaRespiratoria,
            pulso: dados.pulso,
            dor: dados.dor,
            tipo_atendimento: dados.tipoAtendimento,
            tipo_atendimento_label: dados.tipoAtendimentoLabel,
            data_acolhimento: dados.dataAcolhimento,
            profissional_responsavel: dados.profissionalResponsavel,
            profissional_conselho: dados.profissionalConselho,
            profissional_registro: dados.profissionalRegistro,
            profissional_conselho_registro: dados.profissionalConselhoRegistro
        };
    }

    function esconderPassagensDia() {
        if (!alertaPassagensDia) {
            return;
        }

        alertaPassagensDia.classList.add("is-hidden");
        alertaPassagensDia.innerHTML = "";
    }

    function mostrarPassagensDia(passagens) {
        if (!alertaPassagensDia) {
            return;
        }

        if (!passagens || !passagens.total) {
            esconderPassagensDia();
            return;
        }

        const linhas = (passagens.passagens || []).map(function (passagem) {
            return `
                <tr>
                    <td>${escaparHtml(passagem.bam)}</td>
                    <td>${escaparHtml(passagem.data)}</td>
                    <td>${escaparHtml(passagem.hora)}</td>
                    <td>${escaparHtml(passagem.tipo)}</td>
                    <td>${escaparHtml(passagem.status)}</td>
                </tr>
            `;
        }).join("");

        alertaPassagensDia.innerHTML = `
            <div class="passagens-dia-topo">
                <div>
                    <strong>Paciente com passagem no hospital hoje</strong>
                    <span>${escaparHtml(passagens.periodo_inicio)} ate ${escaparHtml(passagens.periodo_fim)}</span>
                </div>
                <span class="passagens-dia-total">${passagens.total} registro(s)</span>
            </div>

            <div class="passagens-dia-alerta">
                Confira as passagens anteriores antes de abrir um novo acolhimento.
            </div>

            <div class="passagens-dia-scroll">
                <table class="passagens-dia-tabela">
                    <thead>
                        <tr>
                            <th>BAM</th>
                            <th>Data</th>
                            <th>Hora</th>
                            <th>Tipo</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>
        `;

        alertaPassagensDia.classList.remove("is-hidden");
    }

    if (tabelaPacientes) {
        tabelaPacientes.style.display = "none";
    }

    let timerBuscaPaciente = null;
    let controladorBuscaPaciente = null;

    if (busca && tabela) {
        busca.addEventListener("keyup", function () {
            const texto = this.value.trim();
            clearTimeout(timerBuscaPaciente);

            if (controladorBuscaPaciente) {
                controladorBuscaPaciente.abort();
                controladorBuscaPaciente = null;
            }

            if (texto.length < 2) {
                tabela.innerHTML = "";

                if (tabelaPacientes) {
                    tabelaPacientes.style.display = "none";
                }

                esconderPassagensDia();

                return;
            }

            if (tabelaPacientes) {
                tabelaPacientes.style.display = "table";
            }

            timerBuscaPaciente = setTimeout(function () {
                controladorBuscaPaciente = new AbortController();

                fetch(
                    `/acolhimento/buscar-paciente/?busca=${encodeURIComponent(texto)}`,
                    {signal: controladorBuscaPaciente.signal}
                )
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        tabela.innerHTML = "";

                        data.forEach(function (paciente) {
                            const passagens = paciente.passagens_hoje || {};
                            const totalPassagens = passagens.total || 0;
                            const passagensCodificadas = encodeURIComponent(JSON.stringify(passagens));

                            tabela.innerHTML += `
                                <tr
                                    data-nome="${escaparHtml(paciente.nome)}"
                                    data-cpf="${escaparHtml(paciente.cpf)}"
                                    data-data="${escaparHtml(paciente.data_nascimento)}"
                                    data-idade="${escaparHtml(paciente.idade)}"
                                    data-passagens="${passagensCodificadas}">
                                    <td>${escaparHtml(paciente.nome)}</td>
                                    <td>${escaparHtml(paciente.cpf)}</td>
                                    <td>${escaparHtml(paciente.data_nascimento)}</td>
                                    <td>${escaparHtml(paciente.idade)}</td>
                                    <td>
                                        <span class="${totalPassagens > 0 ? "passagens-dia-badge alerta" : "passagens-dia-badge"}">
                                            ${totalPassagens}
                                        </span>
                                    </td>
                                </tr>
                            `;
                        });
                    })
                    .catch(function (erro) {
                        if (erro.name !== "AbortError") {
                            tabela.innerHTML = "";
                        }
                    });
            }, 300);
        });

        tabela.addEventListener("click", function (e) {
            const linha = e.target.closest("tr");

            if (!linha) {
                return;
            }

            const nomePaciente = document.getElementById("nome_paciente");
            const cpfPaciente = document.getElementById("cpf");
            const dataNascimentoPaciente = document.getElementById("data_nascimento");
            const idadePaciente = document.getElementById("idade");

            if (nomePaciente) {
                nomePaciente.value = linha.dataset.nome;
            }

            if (cpfPaciente) {
                cpfPaciente.value = linha.dataset.cpf;
            }

            if (dataNascimentoPaciente) {
                dataNascimentoPaciente.value = linha.dataset.data;
            }

            if (idadePaciente) {
                idadePaciente.value = linha.dataset.idade;
            }

            try {
                mostrarPassagensDia(JSON.parse(decodeURIComponent(linha.dataset.passagens || "")));
            } catch (erro) {
                esconderPassagensDia();
            }

            busca.value = "";
            tabela.innerHTML = "";

            if (tabelaPacientes) {
                tabelaPacientes.style.display = "none";
            }

            const pacienteBox = document.querySelector(".paciente-box");

            if (pacienteBox) {
                window.scrollTo({
                    top: pacienteBox.offsetTop - 50,
                    behavior: "smooth"
                });
            }
        });
    }

    // =========================
    // VALIDAR SINAIS VITAIS
    // =========================
    const formulario = document.querySelector("form");

    if (formulario) {
        formulario.addEventListener("submit", function (e) {
            const temperaturaCampo = document.querySelector('[name="temperatura"]');
            const frCampo = document.querySelector('[name="frequencia_respiratoria"]');
            const pulsoCampo = document.querySelector('[name="pulso"]');
            const dorCampo = document.querySelector('[name="dor"]');

            if (!temperaturaCampo || !frCampo || !pulsoCampo || !dorCampo) {
                return;
            }

            const temperatura = parseFloat(temperaturaCampo.value.replace(",", "."));
            const fr = parseInt(frCampo.value);
            const pulso = parseInt(pulsoCampo.value);
            const dor = parseInt(dorCampo.value);

            if (temperatura < 34 || temperatura > 42) {
                alert("Temperatura inválida.");
                e.preventDefault();
                return;
            }

            if (fr < 5 || fr > 60) {
                alert("Frequência respiratória inválida.");
                e.preventDefault();
                return;
            }

            if (pulso < 20 || pulso > 250) {
                alert("Pulso inválido.");
                e.preventDefault();
                return;
            }

            if (dor < 0 || dor > 10) {
                alert("Dor deve ser entre 0 e 10.");
                e.preventDefault();
                return;
            }

        });
    }

    // =========================
    // ENTER = PRÓXIMO CAMPO
    // =========================
    const campos = Array.from(
        document.querySelectorAll("input, select, textarea")
    ).filter(function (campo) {
        return !campo.disabled && campo.type !== "hidden" && !campo.readOnly;
    });

    campos.forEach(function (campo, index) {
        campo.addEventListener("keydown", function (e) {
            if (e.key !== "Enter") {
                return;
            }

            e.preventDefault();

            const proximoCampo = campos[index + 1];

            if (proximoCampo) {
                proximoCampo.focus();
            }
        });
    });

    // =========================
    // MODAL DE SUCESSO
    // =========================
    const modal = document.getElementById("modal-sucesso");
    const btnImprimirAcolhimento = document.getElementById("btn-imprimir-acolhimento");
    const dadosImpressaoAcolhimento = obterDadosImpressaoSalva();

    if (btnImprimirAcolhimento && dadosImpressaoAcolhimento) {
        btnImprimirAcolhimento.addEventListener("click", function () {
            if (imprimirDadosPaciente(dadosImpressaoAcolhimento)) {
                fecharModal();
            }
        });
    }

    document.querySelectorAll("[data-reimprimir-acolhimento]").forEach(function (botao) {
        botao.addEventListener("click", function () {
            imprimirDadosPaciente(dadosReimpressaoDoBotao(botao));
        });
    });

    document.querySelectorAll("[data-modal-close]").forEach(function (botao) {
        botao.addEventListener("click", fecharModal);
    });

    if (modal) {
        modal.style.display = "flex";
    }

    // =========================
    // ABAS
    // =========================
    const botoes = document.querySelectorAll(".aba-btn");
    const abas = document.querySelectorAll(".conteudo-aba");

    botoes.forEach(function (botao) {
        botao.addEventListener("click", function () {
            const alvo = botao.dataset.aba;

            botoes.forEach(function (item) {
                item.classList.remove("active");
            });

            abas.forEach(function (aba) {
                aba.classList.remove("active");
            });

            botao.classList.add("active");

            const abaSelecionada = document.getElementById(alvo);

            if (abaSelecionada) {
                abaSelecionada.classList.add("active");
            }
        });
    });
});
// =========================
// HISTÓRICO COM CÓDIGO
// =========================
const CODIGO_HISTORICO = "1234";

const btnAdminHistorico = document.getElementById("btn-admin-historico");
const btnAbaHistorico = document.getElementById("btn-aba-historico");
const modalHistorico = document.getElementById("modal-historico");
const inputCodigoHistorico = document.getElementById("codigo-historico");
const confirmarHistorico = document.getElementById("confirmar-historico");
const cancelarHistorico = document.getElementById("cancelar-historico");
const erroCodigoHistorico = document.getElementById("erro-codigo-historico");

function abrirModalHistorico() {
    if (modalHistorico) {
        modalHistorico.style.display = "flex";
    }

    if (inputCodigoHistorico) {
        inputCodigoHistorico.value = "";
        inputCodigoHistorico.focus();
    }

    if (erroCodigoHistorico) {
        erroCodigoHistorico.textContent = "";
    }
}

function fecharModalHistorico() {
    if (modalHistorico) {
        modalHistorico.style.display = "none";
    }
}

function liberarHistorico() {
    if (!inputCodigoHistorico) {
        return;
    }

    if (inputCodigoHistorico.value !== CODIGO_HISTORICO) {
        if (erroCodigoHistorico) {
            erroCodigoHistorico.textContent = "Código incorreto.";
        }

        inputCodigoHistorico.focus();
        return;
    }

    sessionStorage.setItem("historicoAcolhimentoLiberado", "sim");

    fecharModalHistorico();

    if (btnAbaHistorico) {
        btnAbaHistorico.classList.remove("aba-oculta");
        btnAbaHistorico.click();
    }
}

if (sessionStorage.getItem("historicoAcolhimentoLiberado") === "sim") {
    if (btnAbaHistorico) {
        btnAbaHistorico.classList.remove("aba-oculta");
    }
}

if (btnAdminHistorico) {
    btnAdminHistorico.addEventListener("click", abrirModalHistorico);
}

if (confirmarHistorico) {
    confirmarHistorico.addEventListener("click", liberarHistorico);
}

if (cancelarHistorico) {
    cancelarHistorico.addEventListener("click", fecharModalHistorico);
}

if (inputCodigoHistorico) {
    inputCodigoHistorico.addEventListener("keydown", function (evento) {
        if (evento.key === "Enter") {
            evento.preventDefault();
            liberarHistorico();
        }
    });
}
function fecharModal() {
    const modal = document.getElementById("modal-sucesso");

    if (modal) {
        modal.style.display = "none";
    }
}
