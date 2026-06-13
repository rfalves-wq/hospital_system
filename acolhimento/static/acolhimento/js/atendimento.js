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

    if (!dataNascimento || !idade) return;

    function calcularIdade(data) {
        const nascimento = new Date(data);
        const hoje = new Date();

        let anos = hoje.getFullYear() - nascimento.getFullYear();

        const mes = hoje.getMonth() - nascimento.getMonth();

        if (mes < 0 || (mes === 0 && hoje.getDate() < nascimento.getDate())) {
            anos--;
        }

        return anos;
    }

    dataNascimento.addEventListener("change", function () {
        if (this.value) {
            idade.value = calcularIdade(this.value);
        } else {
            idade.value = "";
        }
    });

});