document.addEventListener("DOMContentLoaded", function () {
    if (!window.InternacaoImpressao) {
        return;
    }

    const dadosImpressao = window.InternacaoImpressao.lerJson("dados-impressao-internacao");
    const modalElemento = document.getElementById("modal-impressao-internacao");
    const botaoImprimir = document.getElementById("btn-imprimir-internacao");

    if (modalElemento && window.bootstrap) {
        const modal = new bootstrap.Modal(modalElemento);
        modal.show();

        modalElemento.addEventListener("hidden.bs.modal", function () {
            const script = document.getElementById("dados-impressao-internacao");

            if (script) {
                script.remove();
            }
        });
    }

    if (botaoImprimir && dadosImpressao) {
        botaoImprimir.addEventListener("click", function () {
            window.InternacaoImpressao.imprimir(dadosImpressao.tipoImpressao, dadosImpressao);

            if (modalElemento && window.bootstrap) {
                bootstrap.Modal.getOrCreateInstance(modalElemento).hide();
            }
        });
    }
});
