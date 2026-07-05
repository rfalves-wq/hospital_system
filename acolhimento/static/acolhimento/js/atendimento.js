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
    const busca = document.getElementById("busca");
    const tabela = document.getElementById("resultado-busca");
    const tabelaPacientes = document.getElementById("tabela-pacientes");

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
                        tabela.innerHTML += `
                            <tr
                                data-nome="${paciente.nome}"
                                data-cpf="${paciente.cpf}"
                                data-data="${paciente.data_nascimento}"
                                data-idade="${paciente.idade}">
                                <td>${paciente.nome}</td>
                                <td>${paciente.cpf}</td>
                                <td>${paciente.data_nascimento}</td>
                                <td>${paciente.idade}</td>
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