(function () {
    if (window.PanicoMedicoInicializado) {
        return;
    }

    const config = window.PanicoMedicoConfig || {};

    if (!config.statusUrl) {
        return;
    }

    window.PanicoMedicoInicializado = true;

    let alertaAtualId = null;
    let banner = null;

    function escapar(texto) {
        const div = document.createElement("div");
        div.textContent = texto || "";
        return div.innerHTML;
    }

    function tokenCsrf() {
        const campo = document.querySelector(
            "#panico-medico-csrf input[name='csrfmiddlewaretoken']"
        );

        if (campo && campo.value) {
            return campo.value;
        }

        const cookie = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith("csrftoken="));

        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    function criarBanner() {
        if (banner) {
            return banner;
        }

        banner = document.createElement("div");
        banner.className = "panico-medico-banner";
        banner.setAttribute("role", "alert");
        banner.setAttribute("aria-live", "assertive");
        document.body.appendChild(banner);

        return banner;
    }

    function textoDetalhe(alerta) {
        const detalhes = [];

        if (alerta.consultorio) {
            detalhes.push(`Local: ${alerta.consultorio}`);
        }

        if (alerta.paciente) {
            detalhes.push(
                alerta.bam
                    ? `Paciente: ${alerta.paciente} - BAM ${alerta.bam}`
                    : `Paciente: ${alerta.paciente}`
            );
        }

        if (alerta.criado_em) {
            detalhes.push(`Acionado em ${alerta.criado_em}`);
        }

        if (alerta.total && alerta.total > 1) {
            detalhes.push(`${alerta.total} alertas ativos`);
        }

        return detalhes.join(" | ");
    }

    function mostrarAlerta(alerta) {
        const elemento = criarBanner();
        alertaAtualId = alerta.id;
        elemento.innerHTML = `
            <div class="panico-medico-inner">
                <div class="panico-medico-pulso" aria-hidden="true"></div>
                <div class="panico-medico-conteudo">
                    <div class="panico-medico-titulo">Alerta de pânico médico</div>
                    <div class="panico-medico-mensagem">
                        ${escapar(alerta.mensagem || "Médico solicitou ajuda imediata.")}
                    </div>
                    <div class="panico-medico-detalhe">
                        ${escapar(textoDetalhe(alerta))}
                    </div>
                </div>
                <div class="panico-medico-acoes">
                    <button type="button" class="panico-medico-encerrar">
                        Encerrar alerta
                    </button>
                </div>
            </div>
        `;
        elemento.classList.add("is-visible");

        const botaoEncerrar = elemento.querySelector(".panico-medico-encerrar");
        if (botaoEncerrar) {
            botaoEncerrar.addEventListener("click", encerrarAlerta);
        }
    }

    function ocultarAlerta() {
        alertaAtualId = null;

        if (banner) {
            banner.classList.remove("is-visible");
        }
    }

    function verificarAlerta() {
        fetch(config.statusUrl, {cache: "no-store"})
            .then((resposta) => resposta.json())
            .then((dados) => {
                if (!dados.ativo) {
                    ocultarAlerta();
                    return;
                }

                if (dados.id !== alertaAtualId || !banner || !banner.classList.contains("is-visible")) {
                    mostrarAlerta(dados);
                }
            })
            .catch(() => {});
    }

    function encerrarAlerta() {
        if (!config.encerrarUrl) {
            return;
        }

        fetch(config.encerrarUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": tokenCsrf(),
                "X-Requested-With": "XMLHttpRequest"
            },
            cache: "no-store"
        })
            .then((resposta) => {
                if (resposta.ok) {
                    ocultarAlerta();
                }
            })
            .catch(() => {});
    }

    verificarAlerta();
    setInterval(verificarAlerta, config.intervalo || 3000);
    document.addEventListener("visibilitychange", () => {
        if (!document.hidden) {
            verificarAlerta();
        }
    });
})();
