document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // MÁSCARA CPF
    // =========================
    const cpf = document.getElementById("cpf");

    if (cpf) {
        cpf.addEventListener("input", function (e) {

            let v = e.target.value.replace(/\D/g, "");

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

    if (dataNascimento && idade) {

        function atualizarIdade() {

            if (!dataNascimento.value) {
                idade.value = "";
                return;
            }

            idade.value = calcularIdade(
                dataNascimento.value
            );
        }

        dataNascimento.addEventListener(
            "change",
            atualizarIdade
        );

        dataNascimento.addEventListener(
            "input",
            atualizarIdade
        );
    }

    // =========================
    // BUSCA AUTOMÁTICA
    // =========================
    const busca = document.getElementById("busca");
    const tabela = document.getElementById("resultado-busca");
    const tabelaPacientes =
        document.getElementById("tabela-pacientes");

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

            fetch(
                `/acolhimento/buscar-paciente/?busca=${texto}`
            )
                .then(response => response.json())
                .then(data => {

                    tabela.innerHTML = "";

                    data.forEach(paciente => {

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

        // =========================
        // SELECIONAR PACIENTE
        // =========================
        tabela.addEventListener("click", function (e) {

            const linha = e.target.closest("tr");

            if (!linha) return;

            document.getElementById(
                "nome_paciente"
            ).value = linha.dataset.nome;

            document.getElementById(
                "cpf"
            ).value = linha.dataset.cpf;

            document.getElementById(
                "data_nascimento"
            ).value = linha.dataset.data;

            document.getElementById(
                "idade"
            ).value = linha.dataset.idade;

            // limpa busca
            busca.value = "";

            // esconde tabela
            tabela.innerHTML = "";

            if (tabelaPacientes) {
                tabelaPacientes.style.display = "none";
            }

            window.scrollTo({
                top: document.querySelector(".paciente-box").offsetTop - 50,
                behavior: "smooth"
            });
        });
    }
});

document.querySelector("form").addEventListener("submit", function(e){

    const temperatura =
        parseFloat(document.querySelector(
            '[name="temperatura"]'
        ).value.replace(",", "."));

    const fr =
        parseInt(document.querySelector(
            '[name="frequencia_respiratoria"]'
        ).value);

    const pulso =
        parseInt(document.querySelector(
            '[name="pulso"]'
        ).value);

    const dor =
        parseInt(document.querySelector(
            '[name="dor"]'
        ).value);

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

// =========================
// ENTER = PRÓXIMO CAMPO
// =========================

const campos = document.querySelectorAll(
    'input, select, textarea'
);

campos.forEach((campo, index) => {

    campo.addEventListener("keydown", function(e) {

        if (e.key === "Enter") {

            e.preventDefault();

            const proximoCampo = campos[index + 1];

            if (proximoCampo) {
                proximoCampo.focus();
            }
        }

    });

});


function fecharModal(){
    document.getElementById("modal-sucesso").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal-sucesso");
    if(modal){
        modal.style.display = "flex";
    }
});


