document.addEventListener("DOMContentLoaded", function () {
    const botoesAbas = document.querySelectorAll("#abasEstoqueFarmacia [data-bs-toggle='tab']");
    const parametros = new URLSearchParams(window.location.search);
    const abaSalva = localStorage.getItem("abaEstoqueFarmaciaAtiva");
    const abaInicial = parametros.toString() ? "#aba-medicamentos" : abaSalva;

    if (abaInicial) {
        const botaoAba = document.querySelector(`[data-bs-target="${abaInicial}"]`);

        if (botaoAba) {
            new bootstrap.Tab(botaoAba).show();
        }
    }

    botoesAbas.forEach(function (botao) {
        botao.addEventListener("shown.bs.tab", function (evento) {
            localStorage.setItem(
                "abaEstoqueFarmaciaAtiva",
                evento.target.getAttribute("data-bs-target")
            );
        });
    });
});
