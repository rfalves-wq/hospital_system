(function () {
    function limparSelecaoImpressao() {
        document.body.classList.remove("print-section-mode");

        document.querySelectorAll(".print-target.print-active").forEach(function (elemento) {
            elemento.classList.remove("print-active");
        });
    }

    function imprimirTudo() {
        limparSelecaoImpressao();
        window.print();
    }

    function imprimirSecao(seletor) {
        var secao = document.querySelector(seletor);

        if (!secao) {
            return;
        }

        limparSelecaoImpressao();
        secao.classList.add("print-active");
        document.body.classList.add("print-section-mode");
        window.print();
    }

    document.querySelectorAll("[data-print-prontuario]").forEach(function (botao) {
        botao.addEventListener("click", imprimirTudo);
    });

    document.querySelectorAll("[data-print-section]").forEach(function (botao) {
        botao.addEventListener("click", function () {
            imprimirSecao(botao.dataset.printSection);
        });
    });

    window.addEventListener("afterprint", limparSelecaoImpressao);
}());
