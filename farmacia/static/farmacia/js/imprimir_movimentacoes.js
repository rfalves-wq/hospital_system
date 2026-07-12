document.addEventListener("DOMContentLoaded", function () {
    const botaoImprimir = document.querySelector("[data-print-page]");
    const botaoFechar = document.querySelector("[data-close-page]");
    const autoPrint = document.body.dataset.autoPrint === "true";

    if (botaoImprimir) {
        botaoImprimir.addEventListener("click", function () {
            window.print();
        });
    }

    if (botaoFechar) {
        botaoFechar.addEventListener("click", function () {
            window.close();
        });
    }

    if (autoPrint) {
        window.setTimeout(function () {
            window.print();
        }, 350);
    }
});
