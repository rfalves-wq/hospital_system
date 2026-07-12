document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-confirm-submit]").forEach(function (botao) {
        botao.addEventListener("click", function (evento) {
            const mensagem = this.getAttribute("data-confirm-submit") || "Confirmar ação?";

            if (!confirm(mensagem)) {
                evento.preventDefault();
            }
        });
    });

    const botoesAbas = document.querySelectorAll('[data-bs-toggle="tab"]');
    const abaSalva = localStorage.getItem("abaMedicoDashboardAtiva");

    if (abaSalva) {
        const botaoAba = document.querySelector(`[data-bs-target="${abaSalva}"]`);

        if (botaoAba) {
            const aba = new bootstrap.Tab(botaoAba);
            aba.show();
        }
    }

    botoesAbas.forEach(function (botao) {
        botao.addEventListener("shown.bs.tab", function (evento) {
            const destino = evento.target.getAttribute("data-bs-target");
            localStorage.setItem("abaMedicoDashboardAtiva", destino);
        });
    });

    if (window.MedicoImpressao) {
        const dadosImpressao = window.MedicoImpressao.lerJson("dados-impressao-medico");
        const modalElemento = document.getElementById("modal-impressao-medico");
        const botaoImprimir = document.getElementById("btn-imprimir-medico");

        if (modalElemento && window.bootstrap) {
            const modal = new bootstrap.Modal(modalElemento);
            modal.show();

            modalElemento.addEventListener("hidden.bs.modal", function () {
                const script = document.getElementById("dados-impressao-medico");

                if (script) {
                    script.remove();
                }
            });
        }

        if (botaoImprimir && dadosImpressao) {
            botaoImprimir.addEventListener("click", function () {
                window.MedicoImpressao.imprimirTudo(dadosImpressao);

                if (modalElemento && window.bootstrap) {
                    bootstrap.Modal.getOrCreateInstance(modalElemento).hide();
                }
            });
        }
    }
});
