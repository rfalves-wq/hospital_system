document.addEventListener("DOMContentLoaded", function () {
    const configFarmaciaLiberar = document.getElementById("farmacia-liberar-config");
    const exigirBaixa = configFarmaciaLiberar ? configFarmaciaLiberar.dataset.exigirBaixa === "true" : true;
    const buscarMedicamentoEstoqueUrl = configFarmaciaLiberar ? configFarmaciaLiberar.dataset.buscarMedicamentoEstoqueUrl : "";
    const form = document.getElementById("formFarmacia");
    const botao = document.getElementById("btnLiberarFarmacia");
    const btnCopiarPrescricao = document.getElementById("btnCopiarPrescricao");
    const prescricaoMedica = document.getElementById("prescricaoMedica");
    const medicamentosDispensados = document.getElementById("id_medicamentos_dispensados");
    const quantidadeFarmacia = document.getElementById("id_quantidade_farmacia");
    const busca = document.getElementById("buscaMedicamentoEstoque");
    const categoria = document.getElementById("categoriaMedicamentoEstoque");
    const metodo = document.getElementById("metodoMedicamentoEstoque");
    const lista = document.getElementById("listaMedicamentosEstoque");
    const status = document.getElementById("statusMedicamentoEstoque");
    const hiddenItens = document.getElementById("id_itens_estoque_json");
    const itensBody = document.getElementById("itensBaixaBody");

    let timerBusca = null;
    let numeroBusca = 0;
    let itensBaixa = [];

    function definirStatus(texto, alerta) {
        if (!status) return;
        status.textContent = texto;
        status.classList.toggle("alerta", Boolean(alerta));
    }

    function limparLista() {
        if (!lista) return;
        lista.innerHTML = "";
        lista.classList.remove("is-active");
    }

    function numeroInteiro(valor) {
        const texto = String(valor || "0").trim();

        if (!/^\d+$/.test(texto)) {
            return 0;
        }

        const numero = Number.parseInt(texto, 10);
        return Number.isFinite(numero) ? numero : 0;
    }

    function formatarQuantidade(valor) {
        return String(numeroInteiro(valor));
    }

    function montarDetalhe(medicamento) {
        const detalhes = [];

        if (medicamento.categoria) detalhes.push(`Categoria: ${medicamento.categoria}`);
        if (medicamento.metodo) detalhes.push(`Metodo: ${medicamento.metodo}`);
        if (medicamento.principio_ativo) detalhes.push(`Principio ativo: ${medicamento.principio_ativo}`);
        if (medicamento.lote) detalhes.push(`Lote: ${medicamento.lote}`);
        if (medicamento.validade) detalhes.push(`Validade: ${medicamento.validade}`);
        if (medicamento.validade && medicamento.dias_validade) detalhes.push(medicamento.dias_validade);
        if (medicamento.localizacao) detalhes.push(`Local: ${medicamento.localizacao}`);

        return detalhes.join(" | ");
    }

    function atualizarResumoDispensacao() {
        if (hiddenItens) {
            hiddenItens.value = JSON.stringify(
                itensBaixa.map(function (item) {
                    return {
                        medicamento_id: item.id,
                        quantidade: item.quantidade,
                        nome: item.nome,
                        unidade: item.unidade,
                        estoque: item.estoque,
                    };
                })
            );
        }

        if (medicamentosDispensados && itensBaixa.length > 0) {
            medicamentosDispensados.value = itensBaixa.map(function (item) {
                return `${item.nome} - ${formatarQuantidade(item.quantidade)} ${item.unidade}`;
            }).join("\n");
        }

        if (quantidadeFarmacia && itensBaixa.length > 0) {
            quantidadeFarmacia.value = itensBaixa.map(function (item) {
                return `${formatarQuantidade(item.quantidade)} ${item.unidade}`;
            }).join(" / ");
        }
    }

    function renderizarSelecionados() {
        if (!itensBody) return;

        itensBody.innerHTML = "";

        if (itensBaixa.length === 0) {
            const vazio = document.createElement("tr");
            vazio.innerHTML = `
                <td colspan="4" class="selecionados-vazio">
                    Nenhum medicamento selecionado para baixa.
                </td>
            `;
            itensBody.appendChild(vazio);
            atualizarResumoDispensacao();
            return;
        }

        itensBaixa.forEach(function (item) {
            const linha = document.createElement("tr");

            const colMedicamento = document.createElement("td");
            colMedicamento.innerHTML = `
                <div class="estoque-nome"></div>
                <div class="estoque-detalhe">Estoque disponivel: ${item.estoque} ${item.unidade}</div>
            `;
            colMedicamento.querySelector(".estoque-nome").textContent = item.nome;

            const colQuantidade = document.createElement("td");
            const input = document.createElement("input");
            input.type = "number";
            input.className = "form-control form-control-sm qtd-baixa";
            input.min = "1";
            input.step = "1";
            input.value = item.quantidade;
            input.addEventListener("input", function () {
                item.quantidade = this.value;
                atualizarResumoDispensacao();
            });
            colQuantidade.appendChild(input);

            const colUnidade = document.createElement("td");
            colUnidade.textContent = item.unidade || "-";

            const colAcao = document.createElement("td");
            const botaoRemover = document.createElement("button");
            botaoRemover.type = "button";
            botaoRemover.className = "btn btn-outline-danger btn-sm fw-bold";
            botaoRemover.textContent = "Remover";
            botaoRemover.addEventListener("click", function () {
                itensBaixa = itensBaixa.filter(function (selecionado) {
                    return selecionado.id !== item.id;
                });

                renderizarSelecionados();
            });
            colAcao.appendChild(botaoRemover);

            linha.appendChild(colMedicamento);
            linha.appendChild(colQuantidade);
            linha.appendChild(colUnidade);
            linha.appendChild(colAcao);

            itensBody.appendChild(linha);
        });

        atualizarResumoDispensacao();
    }

    function adicionarItemBaixa(medicamento, quantidade) {
        const quantidadeNumero = numeroInteiro(quantidade);

        if (quantidadeNumero <= 0) {
            alert("Informe uma quantidade inteira maior que zero.");
            return;
        }

        const existente = itensBaixa.find(function (item) {
            return item.id === medicamento.id;
        });

        if (existente) {
            existente.quantidade = String(numeroInteiro(existente.quantidade) + quantidadeNumero);
        } else {
            itensBaixa.push({
                id: medicamento.id,
                nome: medicamento.nome,
                unidade: medicamento.unidade || "unidade",
                estoque: medicamento.estoque,
                quantidade: String(quantidadeNumero),
            });
        }

        renderizarSelecionados();
    }

    function renderizarMedicamentos(dados) {
        limparLista();

        const resultados = dados.resultados || [];
        const total = dados.total || 0;

        if (!lista) return;

        if (resultados.length === 0) {
            lista.classList.add("is-active");
            lista.innerHTML = `<div class="p-3 text-muted fw-bold">Nenhum medicamento encontrado.</div>`;
            definirStatus("Nenhum medicamento encontrado.", true);
            return;
        }

        resultados.forEach(function (medicamento) {
            const item = document.createElement("div");
            item.className = "estoque-item";

            const conteudo = document.createElement("div");
            const nome = document.createElement("div");
            nome.className = "estoque-nome";
            nome.textContent = medicamento.nome || "-";

            const detalhe = document.createElement("div");
            detalhe.className = "estoque-detalhe";
            detalhe.textContent = montarDetalhe(medicamento);

            conteudo.appendChild(nome);
            conteudo.appendChild(detalhe);

            const saldo = document.createElement("div");
            saldo.className = "estoque-saldo";
            saldo.textContent = `${medicamento.estoque} ${medicamento.unidade || ""}`.trim();

            const quantidade = document.createElement("input");
            quantidade.type = "number";
            quantidade.className = "form-control form-control-sm";
            quantidade.min = "1";
            quantidade.step = "1";
            quantidade.value = "1";

            const botaoAdicionar = document.createElement("button");
            botaoAdicionar.type = "button";
            botaoAdicionar.className = "btn btn-outline-primary btn-sm fw-bold";
            botaoAdicionar.textContent = "Adicionar";
            botaoAdicionar.addEventListener("click", function () {
                adicionarItemBaixa(medicamento, quantidade.value);
            });

            item.appendChild(conteudo);
            item.appendChild(saldo);
            item.appendChild(quantidade);
            item.appendChild(botaoAdicionar);

            lista.appendChild(item);
        });

        lista.classList.add("is-active");

        if (total > resultados.length) {
            definirStatus(`Mostrando ${resultados.length} de ${total} medicamento(s). Refine a busca para ver outros itens.`);
        } else {
            definirStatus(`${resultados.length} medicamento(s) encontrado(s).`);
        }
    }

    function buscarMedicamentos() {
        if (!lista) return;

        const termo = busca ? busca.value.trim() : "";
        const categoriaValor = categoria ? categoria.value : "";
        const metodoValor = metodo ? metodo.value : "";

        clearTimeout(timerBusca);

        timerBusca = setTimeout(function () {
            if (termo.length < 2 && !categoriaValor && !metodoValor) {
                limparLista();
                definirStatus("Digite pelo menos 2 letras ou selecione um filtro para buscar no estoque.");
                return;
            }

            const parametros = new URLSearchParams({
                q: termo,
                categoria: categoriaValor,
                metodo_aplicacao: metodoValor,
            });

            const buscaAtual = ++numeroBusca;
            definirStatus("Buscando medicamentos no estoque...");

            fetch(`${buscarMedicamentoEstoqueUrl}?${parametros.toString()}`)
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("Erro ao buscar medicamentos.");
                    }

                    return response.json();
                })
                .then(function (dados) {
                    if (buscaAtual !== numeroBusca) return;
                    renderizarMedicamentos(dados);
                })
                .catch(function () {
                    limparLista();
                    definirStatus("Nao foi possivel consultar o estoque agora.", true);
                });
        }, 250);
    }

    if (btnCopiarPrescricao && prescricaoMedica && medicamentosDispensados) {
        btnCopiarPrescricao.addEventListener("click", function () {
            const texto = prescricaoMedica.value.trim();

            if (!texto || texto === "Sem prescricao informada.") {
                return;
            }

            if (medicamentosDispensados.value.trim().length === 0) {
                medicamentosDispensados.value = texto;
            } else {
                medicamentosDispensados.value = medicamentosDispensados.value.trim() + "\n" + texto;
            }

            medicamentosDispensados.focus();
        });
    }

    if (busca) busca.addEventListener("input", buscarMedicamentos);
    if (categoria) categoria.addEventListener("change", buscarMedicamentos);
    if (metodo) metodo.addEventListener("change", buscarMedicamentos);

    if (hiddenItens && hiddenItens.value) {
        try {
            const itensSalvos = JSON.parse(hiddenItens.value);

            if (Array.isArray(itensSalvos)) {
                itensBaixa = itensSalvos.map(function (item) {
                    return {
                        id: Number(item.medicamento_id),
                        nome: item.nome || `Medicamento #${item.medicamento_id}`,
                        unidade: item.unidade || "unidade",
                        estoque: item.estoque || "-",
                        quantidade: String(item.quantidade || "1"),
                    };
                }).filter(function (item) {
                    return item.id > 0;
                });
            }
        } catch (erro) {
            itensBaixa = [];
        }
    }

    renderizarSelecionados();

    if (form && botao) {
        form.addEventListener("submit", function (event) {
            if (exigirBaixa && itensBaixa.length === 0) {
                event.preventDefault();
                alert("Selecione pelo menos um medicamento do estoque para dar baixa.");
                return;
            }

            if (!form.checkValidity()) {
                return;
            }

            atualizarResumoDispensacao();
            botao.disabled = true;

            const texto = botao.querySelector(".btn-text");
            const loading = botao.querySelector(".btn-loading");

            if (texto && loading) {
                texto.classList.add("d-none");
                loading.classList.remove("d-none");
            }
        });
    }
});
