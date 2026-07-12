document.addEventListener("DOMContentLoaded", function () {
    const configMedicoAtender = document.getElementById("medico-atender-config");
    const buscarMedicamentoFarmaciaUrl = configMedicoAtender ? configMedicoAtender.dataset.buscarMedicamentoFarmaciaUrl : "";

    document.querySelectorAll("[data-confirm-submit]").forEach(function (botao) {
        botao.addEventListener("click", function (evento) {
            const mensagem = this.getAttribute("data-confirm-submit") || "Confirmar ação?";

            if (!confirm(mensagem)) {
                evento.preventDefault();
            }
        });
    });

    const examesLaboratoriais = [
        "Hemograma Completo",
        "Glicose",
        "Parcial de Urina - EAS",
        "Amilase Total",
        "Gonadotrófico Coriônico Humano Qualitativo - BhCG",
        "Bilirrubina Total e Frações",
        "Creatinina Quinase - MB",
        "Creatinina Fosfoquinase - CK",
        "Troponina",
        "Creatinina",
        "Uréia",
        "Grupo Sanguíneo ABO - Genótipo",
        "Fator RH",
        "Coombs Direto",
        "Fosfatase Alcalina - ALP",
        "Gama Glutamil Transferase - GGT",
        "Aspartato Aminotransferase - TGO",
        "Alanina Aminotransferase - TGP",
        "Coagulograma",
        "TAP",
        "PTT",
        "Sódio Na+",
        "Potássio K+",
        "Proteína C Reativa",
        "Lactato Desidrogenase - LDH",
        "Sorologia para Lues - VDRL",
        "Teste Rápido de Hepatite B - HBsAg",
        "Teste Rápido de HIV",
        "Gasometria"
    ];

    const examesImagem = [
        {
            setor: "RAIO-X",
            classe: "raiox",
            grupos: [
                {
                    nome: "Tórax",
                    exames: [
                        { nome: "TÓRAX", incidencias: ["AP", "PA", "LAT", "OBL"] },
                        { nome: "TÓRAX PED.", incidencias: ["AP", "PA", "LAT", "OBL"] },
                        { nome: "COSTELA D", incidencias: ["AP", "PA", "OBL"] },
                        { nome: "COSTELA E", incidencias: ["AP", "PA", "OBL"] },
                        { nome: "ESTERNO", incidencias: ["LAT", "OBL"] }
                    ]
                },
                {
                    nome: "Abdomen",
                    exames: [
                        { nome: "ABDOMEN", incidencias: ["AP", "PA", "LAT"] },
                        { nome: "ABDOMEN ORTOSTASE", incidencias: ["ORTOSTASE AP", "ORTOSTASE PA", "SUPINO AP", "SUPINO PA"] }
                    ]
                },
                {
                    nome: "Coluna",
                    exames: [
                        { nome: "COLUNA CERVICAL", incidencias: ["AP", "LAT", "OBL"] },
                        { nome: "COLUNA CERVICAL FLEXÃO / EXTENSÃO", incidencias: ["FLEXÃO", "EXTENSÃO"] },
                        { nome: "COLUNA TORÁCICA", incidencias: ["AP", "LAT", "OBL"] },
                        { nome: "COLUNA LOMBAR", incidencias: ["AP", "LAT", "OBL"] },
                        { nome: "SACRO", incidencias: ["AP", "LAT"] },
                        { nome: "CÓCCIX", incidencias: ["AP", "LAT"] },
                        { nome: "SACRO ILÍACO", incidencias: ["AP", "OBL"] }
                    ]
                },
                {
                    nome: "Extremidade Superior",
                    exames: [
                        { nome: "MÃO D", incidencias: ["PA", "OBL", "LAT"] },
                        { nome: "MÃO E", incidencias: ["PA", "OBL", "LAT"] },
                        { nome: "PUNHO D", incidencias: ["PA", "OBL", "LAT", "NAVICULAR", "FLEXÃO ULNAR", "FLEXÃO RADIAL"] },
                        { nome: "PUNHO E", incidencias: ["PA", "OBL", "LAT", "NAVICULAR", "FLEXÃO ULNAR", "FLEXÃO RADIAL"] },
                        { nome: "ANTEBRAÇO D", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "ANTEBRAÇO E", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "COTOVELO D", incidencias: ["AP", "OBL", "LAT", "AXIAL"] },
                        { nome: "COTOVELO E", incidencias: ["AP", "OBL", "LAT", "AXIAL"] },
                        { nome: "ÚMERO D", incidencias: ["AP", "LAT"] },
                        { nome: "ÚMERO E", incidencias: ["AP", "LAT"] },
                        { nome: "OMBRO D", incidencias: ["AP", "ROT. INTERNA", "ROT. EXTERNA", "AXILAR", "PERFIL Y", "OBL"] },
                        { nome: "OMBRO E", incidencias: ["AP", "ROT. INTERNA", "ROT. EXTERNA", "AXILAR", "PERFIL Y", "OBL"] },
                        { nome: "ESCÁPULA D", incidencias: ["AP", "AXIAL", "PERFIL Y"] },
                        { nome: "ESCÁPULA E", incidencias: ["AP", "AXIAL", "PERFIL Y"] },
                        { nome: "CLAVÍCULA D", incidencias: ["AP", "PA", "AXIAL"] },
                        { nome: "CLAVÍCULA E", incidencias: ["AP", "PA", "AXIAL"] }
                    ]
                },
                {
                    nome: "Extremidade Inferior",
                    exames: [
                        { nome: "PELVE", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "QUADRIL", incidencias: ["AP", "LAT", "PERNA DE RÃ", "ROT. INTERNA", "ROT. EXTERNA"] },
                        { nome: "FÊMUR D", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "FÊMUR E", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "JOELHO D", incidencias: ["AP", "OBL", "LAT", "AXIAL"] },
                        { nome: "JOELHO E", incidencias: ["AP", "OBL", "LAT", "AXIAL"] },
                        { nome: "PERNA D", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "PERNA E", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "TORNOZELO D", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "TORNOZELO E", incidencias: ["AP", "OBL", "LAT"] },
                        { nome: "CALCANHAR D", incidencias: ["AXIAL", "LAT"] },
                        { nome: "CALCANHAR E", incidencias: ["AXIAL", "LAT"] },
                        { nome: "PÉ D", incidencias: ["AP", "OBL", "LAT", "COM CARGA"] },
                        { nome: "PÉ E", incidencias: ["AP", "OBL", "LAT", "COM CARGA"] },
                        { nome: "PATELA D", incidencias: ["AXIAL", "LAT"] },
                        { nome: "PATELA E", incidencias: ["AXIAL", "LAT"] },
                        { nome: "ESCANOMETRIA", incidencias: ["AP"] }
                    ]
                },
                {
                    nome: "Crânio",
                    exames: [
                        { nome: "CRÂNIO", incidencias: ["AP", "PA", "OBL", "LAT"] },
                        { nome: "SEIOS DA FACE", incidencias: ["AP", "PA", "CALDWELL", "WATERS"] },
                        { nome: "FACIAL", incidencias: ["AP", "PA", "CALDWELL", "LAT", "SMV"] },
                        { nome: "OSSO NASAL", incidencias: ["PA", "AP WATERS", "LAT. D", "LAT. E", "LAT"] },
                        { nome: "CAVUM", incidencias: ["BOCA ABERTA", "BOCA FECHADA"] },
                        { nome: "MANDÍBULA", incidencias: ["AP", "PA", "TOWNE"] },
                        { nome: "TEMP-MANDÍBULA", incidencias: ["AP", "OBL", "PA", "TOWNE", "BOCA ABERTA", "BOCA FECHADA"] },
                        { nome: "ZIGOMÁTICO", incidencias: ["AP", "PA", "LAT"] },
                        { nome: "SELA", incidencias: ["AP", "PA", "LAT", "SMV"] }
                    ]
                }
            ]
        },
        {
            setor: "TOMOGRAFIA",
            classe: "tomografia",
            grupos: [
                {
                    nome: "Cabeça e Pescoço",
                    exames: [
                        { nome: "Crânio" },
                        { nome: "Mastoidite" },
                        { nome: "Face" },
                        { nome: "Seios da Face" },
                        { nome: "ATM" },
                        { nome: "Pescoço" }
                    ]
                },
                {
                    nome: "Tórax, Abdome e Pelve",
                    exames: [
                        { nome: "Tórax" },
                        { nome: "Arcos costais" },
                        { nome: "Abdômen superior" },
                        { nome: "Pelve" },
                        { nome: "Bacia / Quadril" },
                        { nome: "Urotomografia" }
                    ]
                },
                {
                    nome: "Colunas",
                    exames: [
                        { nome: "Coluna cervical" },
                        { nome: "Coluna torácica" },
                        { nome: "Coluna lombar" },
                        { nome: "Sacro cóccix" }
                    ]
                },
                {
                    nome: "Membros Superiores e Inferiores",
                    exames: [
                        { nome: "Mão" },
                        { nome: "Punho" },
                        { nome: "Cotovelo" },
                        { nome: "Antebraço" },
                        { nome: "Braço" },
                        { nome: "Ombro" },
                        { nome: "Fêmur" },
                        { nome: "Joelho" },
                        { nome: "Perna" },
                        { nome: "Tornozelo" },
                        { nome: "Pé" }
                    ]
                }
            ]
        },
        {
            setor: "MAMOGRAFIA",
            classe: "mamografia",
            grupos: [
                {
                    nome: "Mama",
                    exames: [
                        {
                            nome: "Mama",
                            incidencias: [
                                "Craniocaudal direita (CCD)",
                                "Craniocaudal esquerda (CCE)",
                                "Médio lateral oblíquo direita (MLOD)",
                                "Médio lateral oblíqua esquerda (MLOE)",
                                "Médio lateral direita (MLD)",
                                "Médio lateral esquerda (MLE)"
                            ]
                        }
                    ]
                }
            ]
        },
        {
            setor: "DENSITOMETRIA",
            classe: "densitometria",
            grupos: [
                {
                    nome: "Densitometria óssea",
                    exames: [
                        { nome: "Coluna lombar" },
                        { nome: "Fêmur" },
                        { nome: "Antebraço" }
                    ]
                }
            ]
        }
    ];

    function normalizarTexto(texto) {
        return String(texto || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function codigoCidEhAgressao(codigo) {
        const limpo = String(codigo || "")
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, "");

        const partes = limpo.match(/^([A-Z])(\d{2})/);

        if (!partes) {
            return false;
        }

        const letra = partes[1];
        const numero = parseInt(partes[2], 10);

        return (
            (letra === "X" && numero >= 85 && numero <= 99) ||
            (letra === "Y" && numero >= 0 && numero <= 9)
        );
    }

    function cidEhAgressao(codigo, descricao) {
        const texto = normalizarTexto(`${codigo} ${descricao}`);

        return codigoCidEhAgressao(codigo) || texto.includes("agress");
    }

    function atualizarAlertaCidAgressao(codigo, descricao) {
        const buscaCid = document.getElementById("busca_cid");
        const cidInput = document.getElementById("id_cid");
        const alerta = document.getElementById("alerta-cid-agressao");

        const ehAgressao = cidEhAgressao(codigo, descricao);

        if (buscaCid) {
            buscaCid.classList.toggle("cid-agressao", ehAgressao);
        }

        if (cidInput) {
            cidInput.classList.toggle("cid-agressao", ehAgressao);
        }

        if (alerta) {
            alerta.classList.toggle("d-none", !ehAgressao);
        }
    }

    function criarId(texto) {
        return texto
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/(^-|-$)/g, "");
    }

    function renderizarLaboratorio() {
        const lista = document.getElementById("listaLaboratorio");

        if (!lista) return;

        examesLaboratoriais.forEach(function (exame) {
            const label = document.createElement("label");
            label.className = "exam-option";
            label.innerHTML = `<input type="checkbox" value="${exame}"> ${exame}`;
            lista.appendChild(label);
        });
    }

    function renderizarImagem() {
        const lista = document.getElementById("listaImagem");

        if (!lista) return;

        examesImagem.forEach(function (setor) {
            const setorId = `setor-${criarId(setor.setor)}`;

            const botaoSetor = document.createElement("button");
            botaoSetor.type = "button";
            botaoSetor.className = `exam-sector-toggle ${setor.classe}`;
            botaoSetor.setAttribute("data-target", `#${setorId}`);
            botaoSetor.innerHTML = `${setor.setor} <span class="toggle-symbol">+</span>`;

            const corpoSetor = document.createElement("div");
            corpoSetor.id = setorId;
            corpoSetor.className = "exam-master-body is-hidden";

            setor.grupos.forEach(function (grupo) {
                const grupoId = `${setorId}-${criarId(grupo.nome)}`;

                const botaoGrupo = document.createElement("button");
                botaoGrupo.type = "button";
                botaoGrupo.className = "exam-category-toggle";
                botaoGrupo.setAttribute("data-target", `#${grupoId}`);
                botaoGrupo.innerHTML = `${grupo.nome} <span class="toggle-symbol">+</span>`;

                const corpoGrupo = document.createElement("div");
                corpoGrupo.id = grupoId;
                corpoGrupo.className = "exam-category-body is-hidden";

                grupo.exames.forEach(function (exame) {
                    if (exame.incidencias && exame.incidencias.length > 0) {
                        const card = document.createElement("div");
                        card.className = "exam-with-views";
                        card.setAttribute("data-sector", setor.setor);
                        card.setAttribute("data-exam", exame.nome);

                        const incidencias = exame.incidencias.map(function (incidencia) {
                            return `<label><input type="checkbox" class="exam-view" value="${incidencia}"> ${incidencia}</label>`;
                        }).join("");

                        card.innerHTML = `
                            <div class="exam-title">${exame.nome}</div>
                            <div class="exam-views">${incidencias}</div>
                        `;

                        corpoGrupo.appendChild(card);
                    } else {
                        const label = document.createElement("label");
                        label.className = "exam-option";
                        label.setAttribute("data-sector", setor.setor);
                        label.innerHTML = `<input type="checkbox" value="${exame.nome}"> ${exame.nome}`;
                        corpoGrupo.appendChild(label);
                    }
                });

                corpoSetor.appendChild(botaoGrupo);
                corpoSetor.appendChild(corpoGrupo);
            });

            lista.appendChild(botaoSetor);
            lista.appendChild(corpoSetor);
        });
    }

    function configurarAbas() {
        const botoesAbas = document.querySelectorAll('[data-bs-toggle="tab"]');
        const abaSalva = localStorage.getItem("abaConsultaMedicaAtiva");

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
                localStorage.setItem("abaConsultaMedicaAtiva", destino);
            });
        });
    }

    function configurarAcordeonExames() {
        document.addEventListener("click", function (evento) {
            const botao = evento.target.closest(".exam-sector-toggle, .exam-category-toggle");

            if (!botao) return;

            const alvo = document.querySelector(botao.getAttribute("data-target"));
            const simbolo = botao.querySelector(".toggle-symbol");

            if (!alvo) return;

            alvo.classList.toggle("is-hidden");
            botao.classList.toggle("open", !alvo.classList.contains("is-hidden"));

            if (simbolo) {
                simbolo.textContent = alvo.classList.contains("is-hidden") ? "+" : "-";
            }
        });
    }

    function configurarBuscaCid() {
        const buscaCid = document.getElementById("busca_cid");
        const cidInput = document.getElementById("id_cid");
        const resultadoCid = document.getElementById("resultado-cid");

        let timerCid = null;

        if (!buscaCid || !cidInput || !resultadoCid) return;

        if (cidInput.value) {
            buscaCid.value = cidInput.value;
            atualizarAlertaCidAgressao(cidInput.value, buscaCid.value);
        }

        buscaCid.addEventListener("input", function () {
            const termo = this.value.trim();

            atualizarAlertaCidAgressao(termo, termo);

            clearTimeout(timerCid);

            if (termo.length < 2) {
                resultadoCid.innerHTML = "";
                resultadoCid.style.display = "none";

                if (termo.length === 0) {
                    cidInput.value = "";
                    atualizarAlertaCidAgressao("", "");
                }

                return;
            }

            timerCid = setTimeout(function () {
                fetch(`/medico/buscar-cid/?q=${encodeURIComponent(termo)}`)
                    .then(response => response.json())
                    .then(data => {
                        resultadoCid.innerHTML = "";

                        if (data.length === 0) {
                            resultadoCid.innerHTML = `
                                <div class="list-group-item text-muted">
                                    Nenhum CID encontrado.
                                </div>
                            `;
                            resultadoCid.style.display = "block";
                            return;
                        }

                        data.forEach(function (cid) {
                            const item = document.createElement("button");
                            const agressao = cidEhAgressao(cid.codigo, cid.descricao);

                            item.type = "button";
                            item.className = "list-group-item list-group-item-action";

                            if (agressao) {
                                item.classList.add("list-group-item-danger");
                            }

                            item.innerHTML = `
                                <strong>${cid.codigo}</strong> - ${cid.descricao}
                                ${agressao ? "<span class='badge bg-danger ms-2'>Agressão</span>" : ""}
                            `;

                            item.addEventListener("click", function () {
                                cidInput.value = cid.codigo;
                                buscaCid.value = `${cid.codigo} - ${cid.descricao}`;
                                resultadoCid.innerHTML = "";
                                resultadoCid.style.display = "none";

                                atualizarAlertaCidAgressao(cid.codigo, cid.descricao);
                            });

                            resultadoCid.appendChild(item);
                        });

                        resultadoCid.style.display = "block";
                    });
            }, 300);
        });

        document.addEventListener("click", function (event) {
            if (!buscaCid.contains(event.target) && !resultadoCid.contains(event.target)) {
                resultadoCid.style.display = "none";
            }
        });
    }

    function configurarListasExames() {
        const listasExames = document.querySelectorAll(".exam-list");

        listasExames.forEach(function (lista) {
            const modo = lista.getAttribute("data-mode");
            const targetId = lista.getAttribute("data-target");
            const checkPrincipalId = lista.getAttribute("data-check");
            const counterId = lista.getAttribute("data-counter");

            const campoTexto = document.getElementById(targetId);
            const checkPrincipal = document.getElementById(checkPrincipalId);
            const contador = document.getElementById(counterId);

            if (!campoTexto) return;

            const checksSimples = lista.querySelectorAll('.exam-option input[type="checkbox"]');
            const examesComIncidencias = lista.querySelectorAll(".exam-with-views");

            function atualizarContador(total) {
                if (contador) {
                    contador.textContent = `Selecionados: ${total}`;
                }
            }

            function atualizarCampoSimples() {
                const selecionados = [];

                checksSimples.forEach(function (check) {
                    const label = check.closest(".exam-option");

                    if (label) {
                        label.classList.toggle("selected", check.checked);
                    }

                    if (check.checked) {
                        selecionados.push(check.value);
                    }
                });

                campoTexto.value = selecionados.join("\n");

                if (checkPrincipal) {
                    checkPrincipal.checked = selecionados.length > 0;
                }

                atualizarContador(selecionados.length);
            }

            function atualizarCampoPorSetor() {
                const setores = {};
                let totalSelecionados = 0;

                checksSimples.forEach(function (check) {
                    const label = check.closest(".exam-option");
                    const setor = label ? label.getAttribute("data-sector") : "IMAGEM";

                    if (label) {
                        label.classList.toggle("selected", check.checked);
                    }

                    if (check.checked) {
                        if (!setores[setor]) {
                            setores[setor] = [];
                        }

                        setores[setor].push(`${setor} - ${check.value}`);
                        totalSelecionados += 1;
                    }
                });

                examesComIncidencias.forEach(function (grupo) {
                    const setor = grupo.getAttribute("data-sector") || "IMAGEM";
                    const nomeExame = grupo.getAttribute("data-exam");
                    const incidenciasSelecionadas = [];

                    grupo.querySelectorAll(".exam-view").forEach(function (incidencia) {
                        if (incidencia.checked) {
                            incidenciasSelecionadas.push(incidencia.value);
                        }
                    });

                    grupo.classList.toggle("selected", incidenciasSelecionadas.length > 0);

                    if (incidenciasSelecionadas.length > 0) {
                        if (!setores[setor]) {
                            setores[setor] = [];
                        }

                        setores[setor].push(`${setor} - ${nomeExame} - ${incidenciasSelecionadas.join(" / ")}`);
                        totalSelecionados += 1;
                    }
                });

                const textoFinal = [];

                ["RAIO-X", "TOMOGRAFIA", "MAMOGRAFIA", "DENSITOMETRIA"].forEach(function (setor) {
                    if (setores[setor] && setores[setor].length > 0) {
                        textoFinal.push(`--- ${setor} ---`);
                        textoFinal.push(setores[setor].join("\n"));
                    }
                });

                campoTexto.value = textoFinal.join("\n");

                if (checkPrincipal) {
                    checkPrincipal.checked = campoTexto.value.trim().length > 0;
                }

                atualizarContador(totalSelecionados);
            }

            function atualizarCampo() {
                if (modo === "sector") {
                    atualizarCampoPorSetor();
                } else {
                    atualizarCampoSimples();
                }
            }

            checksSimples.forEach(function (check) {
                const label = check.closest(".exam-option");
                const setor = label ? label.getAttribute("data-sector") : "";

                if (modo === "sector") {
                    const linhaEsperada = setor ? `${setor} - ${check.value}` : check.value;

                    if (campoTexto.value.includes(linhaEsperada)) {
                        check.checked = true;
                    }
                } else if (campoTexto.value.includes(check.value)) {
                    check.checked = true;
                }

                if (label) {
                    label.classList.toggle("selected", check.checked);
                }

                check.addEventListener("change", atualizarCampo);
            });

            examesComIncidencias.forEach(function (grupo) {
                const setor = grupo.getAttribute("data-sector") || "IMAGEM";
                const nomeExame = grupo.getAttribute("data-exam");
                const prefixoLinha = `${setor} - ${nomeExame} -`;

                grupo.querySelectorAll(".exam-view").forEach(function (incidencia) {
                    const linhas = campoTexto.value.split(/\r?\n/);
                    const existe = linhas.some(function (linha) {
                        return linha.startsWith(prefixoLinha) && linha.includes(incidencia.value);
                    });

                    if (existe) {
                        incidencia.checked = true;
                    }

                    incidencia.addEventListener("change", atualizarCampo);
                });

                grupo.classList.toggle("selected", Boolean(grupo.querySelector(".exam-view:checked")));
            });

            atualizarCampo();
        });
    }

    function configurarBuscaExames() {
        document.querySelectorAll(".exam-search").forEach(function (input) {
            input.addEventListener("input", function () {
                const lista = document.getElementById(this.getAttribute("data-list-id"));
                const termo = this.value.trim().toLowerCase();

                if (!lista) return;

                lista.querySelectorAll(".exam-option, .exam-with-views").forEach(function (item) {
                    const texto = item.textContent.toLowerCase();
                    item.classList.toggle("is-filter-hidden", termo.length > 0 && !texto.includes(termo));
                });

                if (termo.length > 0) {
                    lista.querySelectorAll(".exam-master-body, .exam-category-body").forEach(function (body) {
                        body.classList.remove("is-hidden");
                    });

                    lista.querySelectorAll(".exam-sector-toggle, .exam-category-toggle").forEach(function (botao) {
                        const simbolo = botao.querySelector(".toggle-symbol");
                        botao.classList.add("open");

                        if (simbolo) {
                            simbolo.textContent = "-";
                        }
                    });
                }
            });
        });
    }

    function configurarLimparExames() {
        document.querySelectorAll("[data-clear-list]").forEach(function (botao) {
            botao.addEventListener("click", function () {
                const lista = document.getElementById(this.getAttribute("data-clear-list"));

                if (!lista) return;

                lista.querySelectorAll('input[type="checkbox"]').forEach(function (check) {
                    check.checked = false;
                    check.dispatchEvent(new Event("change"));
                });
            });
        });
    }

    function configurarMedicamentosFarmacia() {
        const busca = document.getElementById("buscaMedicamentoFarmacia");
        const categoria = document.getElementById("categoriaMedicamentoFarmacia");
        const metodo = document.getElementById("metodoMedicamentoFarmacia");
        const lista = document.getElementById("listaMedicamentosFarmacia");
        const status = document.getElementById("statusMedicamentoFarmacia");
        const campoPrescricao = document.getElementById("id_prescricao");
        const alergiaPaciente = obterAlergiaPaciente();

        if (!lista) {
            return;
        }

        let timerMedicamento = null;
        let numeroBusca = 0;

        function definirStatus(texto, alerta) {
            if (!status) {
                return;
            }

            status.textContent = texto;
            status.classList.toggle("alerta", Boolean(alerta));
        }

        function limparLista() {
            lista.innerHTML = "";
            lista.classList.remove("is-active");
        }

        function montarDetalhe(medicamento) {
            const detalhes = [];

            if (medicamento.categoria) {
                detalhes.push(`Categoria: ${medicamento.categoria}`);
            }

            if (medicamento.metodo) {
                detalhes.push(`Metodo: ${medicamento.metodo}`);
            }

            if (medicamento.principio_ativo) {
                detalhes.push(`Principio ativo: ${medicamento.principio_ativo}`);
            }

            if (medicamento.localizacao) {
                detalhes.push(`Local: ${medicamento.localizacao}`);
            }

            return detalhes.join(" | ");
        }

        function adicionarNaPrescricao(medicamento) {
            if (!campoPrescricao || !medicamento) {
                return;
            }

            if (
                alergiaPaciente
                && !confirm(`Atenção: paciente com alergia registrada:\n\n${alergiaPaciente}\n\nConfirmar uso deste medicamento na prescrição?`)
            ) {
                return;
            }

            const textoAtual = campoPrescricao.value.trim();
            const novaLinha = medicamento + " - ";

            campoPrescricao.value = textoAtual
                ? textoAtual + "\n" + novaLinha
                : novaLinha;

            campoPrescricao.focus();
        }

        function renderizarMedicamentos(dados) {
            limparLista();

            const resultados = dados.resultados || [];
            const total = dados.total || 0;

            if (resultados.length === 0) {
                lista.classList.add("is-active");

                const vazio = document.createElement("div");
                vazio.className = "estoque-farmacia-vazio";
                vazio.textContent = "Nenhum medicamento encontrado com esses filtros.";
                lista.appendChild(vazio);

                definirStatus("Nenhum medicamento encontrado.", true);
                return;
            }

            resultados.forEach(function (medicamento) {
                const item = document.createElement("div");
                item.className = "estoque-farmacia-item";

                const conteudo = document.createElement("div");

                const nome = document.createElement("div");
                nome.className = "estoque-farmacia-nome";
                nome.textContent = medicamento.nome || "-";

                const detalhe = document.createElement("div");
                detalhe.className = "estoque-farmacia-detalhe";
                detalhe.textContent = montarDetalhe(medicamento);

                conteudo.appendChild(nome);
                conteudo.appendChild(detalhe);

                const saldo = document.createElement("div");
                saldo.className = "estoque-farmacia-saldo";
                saldo.textContent = `${medicamento.estoque} ${medicamento.unidade || ""}`.trim();

                const botao = document.createElement("button");
                botao.type = "button";
                botao.className = "btn btn-outline-primary btn-sm fw-bold";
                botao.textContent = "Usar";
                botao.addEventListener("click", function () {
                    adicionarNaPrescricao(medicamento.texto);
                });

                item.appendChild(conteudo);
                item.appendChild(saldo);
                item.appendChild(botao);

                lista.appendChild(item);
            });

            lista.classList.add("is-active");

            if (total > resultados.length) {
                definirStatus(`Mostrando ${resultados.length} de ${total} medicamento(s). Refine a busca para encontrar mais rapido.`);
            } else {
                definirStatus(`${resultados.length} medicamento(s) encontrado(s).`);
            }
        }

        function buscarMedicamentos() {
            const termo = busca ? busca.value.trim() : "";
            const categoriaValor = categoria ? categoria.value : "";
            const metodoValor = metodo ? metodo.value : "";

            clearTimeout(timerMedicamento);

            timerMedicamento = setTimeout(function () {
                if (termo.length < 2 && !categoriaValor && !metodoValor) {
                    limparLista();
                    definirStatus("Digite pelo menos 2 letras ou selecione um filtro para consultar o estoque.");
                    return;
                }

                const parametros = new URLSearchParams({
                    q: termo,
                    categoria: categoriaValor,
                    metodo: metodoValor,
                });

                const buscaAtual = ++numeroBusca;
                definirStatus("Buscando medicamentos no estoque...");

                fetch(`${buscarMedicamentoFarmaciaUrl}?${parametros.toString()}`)
                    .then(function (response) {
                        if (!response.ok) {
                            throw new Error("Erro ao consultar medicamentos.");
                        }

                        return response.json();
                    })
                    .then(function (dados) {
                        if (buscaAtual !== numeroBusca) {
                            return;
                        }

                        renderizarMedicamentos(dados);
                    })
                    .catch(function () {
                        limparLista();
                        definirStatus("Nao foi possivel consultar o estoque da farmacia agora.", true);
                    });
            }, 250);
        }

        if (busca) {
            busca.addEventListener("input", buscarMedicamentos);
        }

        if (categoria) {
            categoria.addEventListener("change", buscarMedicamentos);
        }

        if (metodo) {
            metodo.addEventListener("change", buscarMedicamentos);
        }
    }

    function configurarImpressaoMedica() {
        if (!window.MedicoImpressao) {
            return;
        }

        const baseImpressao = window.MedicoImpressao.lerJson("dados-base-impressao-medico") || {};
        const alergiaPaciente = obterAlergiaPaciente();

        document.querySelectorAll("[data-print-medico]").forEach(function (botao) {
            botao.addEventListener("click", function () {
                const tipo = this.getAttribute("data-print-medico");
                const dados = window.MedicoImpressao.coletarFormulario(baseImpressao);

                if (
                    tipo === "prescricao"
                    && alergiaPaciente
                    && !confirm(`Atenção: paciente com alergia registrada:\n\n${alergiaPaciente}\n\nConfirmar impressão da prescrição?`)
                ) {
                    return;
                }

                window.MedicoImpressao.imprimir(tipo, dados);
            });
        });
    }

    function obterAlergiaPaciente() {
        const alerta = document.getElementById("textoAlergiaPaciente");

        if (!alerta) {
            return "";
        }

        return alerta.textContent.trim();
    }

    function configurarAvisoAlergiaPrescricao() {
        const alergiaPaciente = obterAlergiaPaciente();

        if (!alergiaPaciente) {
            return;
        }

        const campoPrescricao = document.getElementById("id_prescricao");
        const solicitaMedicacao = document.getElementById("id_solicita_medicacao");
        let avisoMostrado = false;

        function avisar() {
            if (avisoMostrado) {
                return;
            }

            avisoMostrado = true;
            alert(`Atenção: paciente com alergia registrada:\n\n${alergiaPaciente}\n\nConfira antes de prescrever medicação.`);
        }

        if (campoPrescricao) {
            campoPrescricao.addEventListener("focus", avisar);
        }

        if (solicitaMedicacao) {
            solicitaMedicacao.addEventListener("change", function () {
                if (this.checked) {
                    avisar();
                }
            });
        }
    }

    function configurarFeedbackFormulario() {
        const formConsulta = document.getElementById("formConsultaMedica");
        const btnSalvar = document.getElementById("btnSalvarConduta");
        const alergiaPaciente = obterAlergiaPaciente();

        function abrirAbaDoCampo(campoId) {
            const campo = document.getElementById(campoId);

            if (!campo) return;

            const painel = campo.closest(".tab-pane");

            if (painel && painel.id) {
                const botaoAba = document.querySelector(`[data-bs-target="#${painel.id}"]`);

                if (botaoAba) {
                    const aba = new bootstrap.Tab(botaoAba);
                    aba.show();
                    localStorage.setItem("abaConsultaMedicaAtiva", `#${painel.id}`);
                }
            }

            setTimeout(function () {
                campo.scrollIntoView({ behavior: "smooth", block: "center" });
                campo.focus({ preventScroll: true });
            }, 250);
        }

        document.querySelectorAll(".erro-campo-link").forEach(function (link) {
            link.addEventListener("click", function (evento) {
                evento.preventDefault();
                abrirAbaDoCampo(this.getAttribute("data-field-id"));
            });
        });

        const primeiroErro = document.querySelector(".tab-pane .errorlist");

        if (primeiroErro) {
            const painel = primeiroErro.closest(".tab-pane");

            if (painel && painel.id) {
                const botaoAba = document.querySelector(`[data-bs-target="#${painel.id}"]`);

                if (botaoAba) {
                    const aba = new bootstrap.Tab(botaoAba);
                    aba.show();
                    localStorage.setItem("abaConsultaMedicaAtiva", `#${painel.id}`);
                }
            }

            const resumo = document.getElementById("formErrorSummary");

            if (resumo) {
                resumo.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        }

        if (formConsulta && btnSalvar) {
            formConsulta.addEventListener("submit", function (evento) {
                const campoPrescricao = document.getElementById("id_prescricao");
                const solicitaMedicacao = document.getElementById("id_solicita_medicacao");
                const temPrescricao = campoPrescricao && campoPrescricao.value.trim().length > 0;
                const vaiUsarMedicacao = solicitaMedicacao && solicitaMedicacao.checked;

                if (
                    alergiaPaciente
                    && (temPrescricao || vaiUsarMedicacao)
                    && !confirm(`Atenção: paciente com alergia registrada:\n\n${alergiaPaciente}\n\nConfirmar salvamento da conduta com prescrição/medicação?`)
                ) {
                    evento.preventDefault();
                    return;
                }

                btnSalvar.disabled = true;

                const texto = btnSalvar.querySelector(".btn-text");
                const loading = btnSalvar.querySelector(".btn-loading");

                if (texto && loading) {
                    texto.classList.add("d-none");
                    loading.classList.remove("d-none");
                }
            });
        }
    }

    renderizarLaboratorio();
    renderizarImagem();

    configurarAbas();
    configurarAcordeonExames();
    configurarBuscaCid();
    configurarListasExames();
    configurarBuscaExames();
    configurarLimparExames();
    configurarMedicamentosFarmacia();
    configurarImpressaoMedica();
    configurarAvisoAlergiaPrescricao();
    configurarFeedbackFormulario();
});
