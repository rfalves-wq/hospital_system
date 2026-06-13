document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log("Tela carregada");

    }
);

document.addEventListener("DOMContentLoaded", function () {

    const cpf = document.getElementById("cpf");

    cpf.addEventListener("input", function (e) {

        let valor = e.target.value.replace(/\D/g, "");

        valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
        valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
        valor = valor.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

        e.target.value = valor;

    });

});

document.addEventListener("DOMContentLoaded", function () {

    const dataNascimento = document.getElementById("data_nascimento");
    const idade = document.getElementById("idade");

    dataNascimento.addEventListener("change", function () {

        if (!this.value) {
            idade.value = "";
            return;
        }

        const nascimento = new Date(this.value);
        const hoje = new Date();

        let anos = hoje.getFullYear() - nascimento.getFullYear();

        const mesAtual = hoje.getMonth();
        const diaAtual = hoje.getDate();

        const mesNascimento = nascimento.getMonth();
        const diaNascimento = nascimento.getDate();

        if (
            mesAtual < mesNascimento ||
            (mesAtual === mesNascimento && diaAtual < diaNascimento)
        ) {
            anos--;
        }

        idade.value = anos + " anos";
    });

});



document.addEventListener("DOMContentLoaded", function () {

    const campos = document.querySelectorAll(
        'input, select, textarea'
    );

    campos.forEach((campo, indice) => {

        campo.addEventListener("keydown", function(e) {

            if (e.key === "Enter") {

                e.preventDefault();

                const proximo = campos[indice + 1];

                if (proximo) {
                    proximo.focus();
                }

            }

        });

    });

});