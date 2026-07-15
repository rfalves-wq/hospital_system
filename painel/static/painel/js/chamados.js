(function () {
    const config = window.painelChamadosConfig || {};
    const ultima = document.getElementById("ultimaChamada");
    const lista = document.getElementById("listaChamadas");
    const relogio = document.getElementById("painelRelogio");
    const botaoVoz = document.getElementById("botaoVozPainel");
    let ultimaId = null;
    let ultimaChamadaAtual = null;
    let vozAtiva = localStorage.getItem("painelChamadosVozAtiva") === "1";
    let sintetizador = window.speechSynthesis || null;
    let vozes = [];

    function escapar(texto) {
        const div = document.createElement("div");
        div.textContent = texto || "";
        return div.innerHTML;
    }

    function atualizarRelogio() {
        const agora = new Date();
        if (relogio) {
            relogio.textContent = agora.toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit"
            });
        }
    }

    function carregarVozes() {
        if (!sintetizador) {
            return;
        }

        vozes = sintetizador.getVoices() || [];
    }

    function vozPortugues() {
        carregarVozes();

        const candidatas = vozes
            .map((voz) => ({voz, pontos: pontuarVoz(voz)}))
            .filter((item) => item.pontos > -1000)
            .sort((a, b) => b.pontos - a.pontos);

        return candidatas.length ? candidatas[0].voz : null;
    }

    function pontuarVoz(voz) {
        const nome = (voz.name || "").toLowerCase();
        const idioma = (voz.lang || "").toLowerCase();

        if (!idioma.startsWith("pt")) {
            return -1000;
        }

        let pontos = idioma === "pt-br" ? 80 : 45;
        const vozesFemininas = [
            "francisca",
            "maria",
            "helena",
            "raquel",
            "luciana",
            "vitoria",
            "vitória",
            "female",
            "feminina",
            "mulher",
            "woman"
        ];
        const vozesNaturais = [
            "natural",
            "online",
            "neural",
            "google",
            "premium"
        ];
        const vozesMasculinas = [
            "antonio",
            "antônio",
            "daniel",
            "felipe",
            "bruno",
            "ricardo",
            "male",
            "masculina",
            "homem",
            "man"
        ];

        if (vozesFemininas.some((termo) => nome.includes(termo))) {
            pontos += 80;
        }

        if (vozesNaturais.some((termo) => nome.includes(termo))) {
            pontos += 35;
        }

        if (vozesMasculinas.some((termo) => nome.includes(termo))) {
            pontos -= 80;
        }

        if (voz.default) {
            pontos += 5;
        }

        return pontos;
    }

    function destinoFalado(chamada) {
        const destino = chamada.local || chamada.setor || "";
        const chave = destino.toLowerCase();
        const nomes = {
            "recepcao": "Recepção",
            "classificacao de risco": "Classificação de risco",
            "consultorio medico": "Consultório médico",
            "medico": "Consultório médico",
            "sala de medicacao": "Sala de medicação"
        };

        if (chave.startsWith("consultorio ")) {
            return destino.replace(/^consultorio/i, "Consultório");
        }

        return nomes[chave] || destino;
    }

    function textoChamada(chamada) {
        const paciente = chamada.paciente || "";
        const destino = destinoFalado(chamada);

        if (chamada.ausencia) {
            return `Paciente ${paciente}, ausente em ${destino}.`;
        }

        if (destino) {
            return `Atenção. Paciente ${paciente}. Comparecer em ${destino}.`;
        }

        return `Atenção. Paciente ${paciente}.`;
    }

    function atualizarBotaoVoz() {
        if (!botaoVoz) {
            return;
        }

        if (!sintetizador || !window.SpeechSynthesisUtterance) {
            botaoVoz.textContent = "Voz indisponível";
            botaoVoz.disabled = true;
            botaoVoz.classList.add("is-unavailable");
            return;
        }

        const voz = vozPortugues();
        botaoVoz.textContent = vozAtiva ? "Voz ativa" : "Ativar voz";
        botaoVoz.title = voz
            ? `Usando voz: ${voz.name}`
            : "Usando a melhor voz em português disponível no navegador";
        botaoVoz.classList.toggle("is-active", vozAtiva);
    }

    function falar(texto, teste, tentativa) {
        if (!vozAtiva || !sintetizador || !window.SpeechSynthesisUtterance || !texto) {
            return;
        }

        tentativa = tentativa || 0;
        const voz = vozPortugues();

        if (!voz && vozes.length === 0 && tentativa < 8) {
            setTimeout(() => falar(texto, teste, tentativa + 1), 250);
            return;
        }

        sintetizador.cancel();

        const fala = new SpeechSynthesisUtterance(texto);
        fala.lang = "pt-BR";
        fala.rate = teste ? .95 : .86;
        fala.pitch = 1.08;
        fala.volume = 1;

        if (voz) {
            fala.voice = voz;
        }

        sintetizador.speak(fala);
    }

    function configurarVoz() {
        localStorage.removeItem("painelChamadosVozURI");
        atualizarBotaoVoz();

        if (!botaoVoz) {
            return;
        }

        botaoVoz.addEventListener("click", () => {
            if (!sintetizador || !window.SpeechSynthesisUtterance) {
                return;
            }

            vozAtiva = !vozAtiva;
            localStorage.setItem("painelChamadosVozAtiva", vozAtiva ? "1" : "0");
            atualizarBotaoVoz();

            if (vozAtiva) {
                falar(
                    ultimaChamadaAtual
                        ? textoChamada(ultimaChamadaAtual)
                        : "Voz do painel ativada.",
                    !ultimaChamadaAtual
                );
            } else {
                sintetizador.cancel();
            }
        });

        if (sintetizador) {
            carregarVozes();
            sintetizador.addEventListener("voiceschanged", () => {
                carregarVozes();
                atualizarBotaoVoz();
            });
            setTimeout(() => {
                carregarVozes();
                atualizarBotaoVoz();
            }, 500);
            setTimeout(() => {
                carregarVozes();
                atualizarBotaoVoz();
            }, 1500);
        }
    }

    function renderUltima(chamada) {
        if (!ultima || !chamada) {
            return;
        }

        ultimaChamadaAtual = chamada;

        const local = chamada.local ? `<span>${escapar(chamada.local)}</span>` : "";
        const classeAusencia = chamada.ausencia ? " call-sector-absence" : "";
        ultima.innerHTML = `
            <div class="call-sector${classeAusencia}">${escapar(chamada.titulo || chamada.setor)}</div>
            <h1>${escapar(chamada.paciente)}</h1>
            <div class="call-details">
                <span>BAM ${escapar(chamada.bam || "-")}</span>
                ${local}
            </div>
        `;

        if (ultimaId && ultimaId !== chamada.id) {
            ultima.classList.remove("pulse");
            void ultima.offsetWidth;
            ultima.classList.add("pulse");
            falar(textoChamada(chamada));
        }

        ultimaId = chamada.id;
    }

    function renderLista(chamadas) {
        if (!lista) {
            return;
        }

        if (!chamadas.length) {
            lista.innerHTML = '<div class="empty-call">Nenhuma chamada registrada.</div>';
            return;
        }

        lista.innerHTML = chamadas.map((chamada) => {
            const local = chamada.local ? ` &bull; ${escapar(chamada.local)}` : "";
            const tipo = chamada.tipo || "chamada";
            return `
                <article class="history-item setor-${escapar(chamada.setor_codigo)} tipo-${escapar(tipo)}">
                    <strong>${escapar(chamada.paciente)}</strong>
                    <span>${escapar(chamada.historico || chamada.setor)}</span>
                    <small>BAM ${escapar(chamada.bam || "-")}${local} &bull; ${escapar(chamada.hora)}</small>
                </article>
            `;
        }).join("");
    }

    function carregar() {
        if (!config.dadosUrl) {
            return;
        }

        fetch(config.dadosUrl, {cache: "no-store"})
            .then((resposta) => resposta.json())
            .then((dados) => {
                if (dados.ultima) {
                    renderUltima(dados.ultima);
                }
                renderLista(dados.chamadas || []);
            })
            .catch(() => {});
    }

    atualizarRelogio();
    configurarVoz();
    carregar();
    setInterval(atualizarRelogio, 1000);
    setInterval(carregar, 5000);
})();
