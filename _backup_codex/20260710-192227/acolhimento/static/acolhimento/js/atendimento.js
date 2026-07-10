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

    function valorCampo(seletor) {
        const campo = document.querySelector(seletor);
        return campo && campo.value ? campo.value : "-";
    }

    function formatarDataBr(valor) {
        if (!valor || !valor.includes("-")) {
            return valor || "-";
        }

        const partes = valor.split("-");

        if (partes.length !== 3) {
            return valor;
        }

        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    function nomeTipoAtendimento(tipo) {
        const tipos = {
            NORMAL: "Atendimento Normal",
            RISCO: "Classificacao de Risco",
            PREFERENCIAL: "Atendimento Preferencial"
        };

        return tipos[tipo] || tipo || "-";
    }

    function imprimirDadosPaciente(tipoAtendimento) {
        const agora = new Date();
        const nomePaciente = valorCampo("#nome_paciente");
        const cpfPaciente = valorCampo("#cpf");
        const dataNascimentoPaciente = formatarDataBr(valorCampo("#data_nascimento"));
        const idadePaciente = valorCampo("#idade");
        const horaChegadaPaciente = valorCampo("#hora_chegada");
        const tipoTexto = nomeTipoAtendimento(tipoAtendimento);

        const pressao = valorCampo('[name="pressao_arterial"]');
        const temperatura = valorCampo('[name="temperatura"]');
        const frequencia = valorCampo('[name="frequencia_respiratoria"]');
        const pulso = valorCampo('[name="pulso"]');
        const dor = valorCampo('[name="dor"]');

        const conteudo = `
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <title>Ficha de Atendimento</title>
                <style>
                    * {
                        box-sizing: border-box;
                    }

                    body {
                        color: #111827;
                        font-family: Arial, Helvetica, sans-serif;
                        margin: 24px;
                    }

                    .cabecalho {
                        border-bottom: 3px solid #0f4c81;
                        margin-bottom: 18px;
                        padding-bottom: 12px;
                    }

                    h1 {
                        color: #0f4c81;
                        font-size: 22px;
                        margin: 0 0 4px;
                    }

                    .subtitulo {
                        color: #475569;
                        font-size: 13px;
                    }

                    .tipo {
                        background: #eaf4ff;
                        border: 1px solid #bfdbfe;
                        border-left: 5px solid #0f4c81;
                        border-radius: 8px;
                        color: #0f4c81;
                        font-size: 18px;
                        font-weight: 800;
                        margin-bottom: 16px;
                        padding: 12px;
                    }

                    .grid {
                        display: grid;
                        grid-template-columns: repeat(2, minmax(0, 1fr));
                        gap: 10px;
                        margin-bottom: 16px;
                    }

                    .item {
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                        padding: 10px;
                    }

                    .item.full {
                        grid-column: 1 / -1;
                    }

                    .label {
                        color: #64748b;
                        font-size: 11px;
                        font-weight: 800;
                        letter-spacing: .04em;
                        margin-bottom: 4px;
                        text-transform: uppercase;
                    }

                    .valor {
                        font-size: 15px;
                        font-weight: 700;
                        word-break: break-word;
                    }

                    .assinatura {
                        margin-top: 44px;
                        text-align: center;
                    }

                    .linha {
                        border-top: 1px solid #111827;
                        display: inline-block;
                        padding-top: 8px;
                        width: 320px;
                    }

                    @media print {
                        body {
                            margin: 12mm;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="cabecalho">
                    <h1>Ficha de Atendimento</h1>
                    <div class="subtitulo">
                        Impresso em ${escaparHtml(agora.toLocaleString("pt-BR"))}
                    </div>
                </div>

                <div class="tipo">${escaparHtml(tipoTexto)}</div>

                <div class="grid">
                    <div class="item full">
                        <div class="label">Paciente</div>
                        <div class="valor">${escaparHtml(nomePaciente)}</div>
                    </div>

                    <div class="item">
                        <div class="label">CPF</div>
                        <div class="valor">${escaparHtml(cpfPaciente)}</div>
                    </div>

                    <div class="item">
                        <div class="label">Nascimento</div>
                        <div class="valor">${escaparHtml(dataNascimentoPaciente)}</div>
                    </div>

                    <div class="item">
                        <div class="label">Idade</div>
                        <div class="valor">${escaparHtml(idadePaciente)} anos</div>
                    </div>

                    <div class="item">
                        <div class="label">Hora da chegada</div>
                        <div class="valor">${escaparHtml(horaChegadaPaciente)}</div>
                    </div>
                </div>

                <div class="grid">
                    <div class="item">
                        <div class="label">Pressao arterial</div>
                        <div class="valor">${escaparHtml(pressao)}</div>
                    </div>

                    <div class="item">
                        <div class="label">Temperatura</div>
                        <div class="valor">${escaparHtml(temperatura)} C</div>
                    </div>

                    <div class="item">
                        <div class="label">Freq. respiratoria</div>
                        <div class="valor">${escaparHtml(frequencia)}</div>
                    </div>

                    <div class="item">
                        <div class="label">Pulso</div>
                        <div class="valor">${escaparHtml(pulso)}</div>
                    </div>

                    <div class="item">
                        <div class="label">Escala de dor</div>
                        <div class="valor">${escaparHtml(dor)} / 10</div>
                    </div>
                </div>

                <div class="assinatura">
                    <span class="linha">Assinatura / Responsavel pelo acolhimento</span>
                </div>
            </body>
            </html>
        `;

        const janela = window.open("", "_blank", "width=820,height=900");

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

    if (busca && tabela) {
        busca.addEventListener("keyup", function () {
            const texto = this.value.trim();

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

            fetch(`/acolhimento/buscar-paciente/?busca=${encodeURIComponent(texto)}`)
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
                });
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

            if (e.submitter && e.submitter.name === "tipo_atendimento") {
                imprimirDadosPaciente(e.submitter.value);
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
