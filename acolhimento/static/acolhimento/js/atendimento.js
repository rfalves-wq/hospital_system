document.addEventListener("DOMContentLoaded", function () {

    console.log("JS carregado");

    // =========================
    // CPF máscara
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
    // IDADE
    // =========================
    const dataNascimento = document.getElementById("data_nascimento");
    const idade = document.getElementById("idade");

    if (dataNascimento && idade) {

        function calcular(data) {
            const nasc = new Date(data);
            const hoje = new Date();

            let anos = hoje.getFullYear() - nasc.getFullYear();

            const m = hoje.getMonth() - nasc.getMonth();

            if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) {
                anos--;
            }

            return anos;
        }

        function atualizar() {
            idade.value = dataNascimento.value
                ? calcular(dataNascimento.value)
                : "";
        }

        dataNascimento.addEventListener("change", atualizar);
        dataNascimento.addEventListener("input", atualizar);
    }

    // =========================
    // ENTER → PRÓXIMO CAMPO (CORRIGIDO)
    // =========================

    const form = document.querySelector("form");

    if (form) {

        const fields = Array.from(
            form.querySelectorAll("input, select, textarea")
        ).filter(el =>
            !el.disabled &&
            el.type !== "hidden" &&
            el.type !== "submit"
        );

        fields.forEach((field, index) => {

            field.addEventListener("keydown", function (e) {

                if (e.key === "Enter") {

                    e.preventDefault();

                    const next = fields[index + 1];

                    if (next) {
                        next.focus();
                    }
                }
            });
        });
    }

});