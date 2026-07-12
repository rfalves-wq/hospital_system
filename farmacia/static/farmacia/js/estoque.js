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

    const checkboxes = Array.from(document.querySelectorAll(".estoque-item-checkbox"));
    const selecionarTodos = document.getElementById("selecionar-todos-estoque");
    const contadorSelecionados = document.getElementById("estoque-bulk-count");
    const botoesLote = Array.from(document.querySelectorAll("[data-bulk-action]"));
    const modalElemento = document.getElementById("modal-movimentacao-lote");

    if (!modalElemento || !checkboxes.length) {
        return;
    }

    const modalLote = new bootstrap.Modal(modalElemento);
    const tipoMovimentacaoInput = document.getElementById("id_lote_tipo_movimentacao");
    const tituloModal = document.getElementById("titulo-modal-movimentacao-lote");
    const subtituloModal = document.getElementById("subtitulo-modal-movimentacao-lote");
    const resumoItens = document.getElementById("resumo-itens-lote");
    const itensContainer = document.getElementById("itens-movimentacao-lote");
    const labelOrigemDestino = document.getElementById("label-origem-destino-lote");
    const origemDestinoInput = document.getElementById("id_origem_destino_movimentacao");
    const botaoConfirmar = document.getElementById("btn-confirmar-movimentacao-lote");

    const configuracoesTipo = {
        ENTRADA: {
            titulo: "Entrada em lote",
            subtitulo: "Informe quanto entrou para cada medicamento selecionado.",
            quantidadeLabel: "Quantidade que entrou",
            quantidadeMin: "1",
            quantidadeInicial: "1",
            origemLabel: "Origem",
            origemPlaceholder: "Fornecedor, compra ou transferencia",
            botao: "Salvar entrada",
            botaoClasse: "btn-success"
        },
        SAIDA: {
            titulo: "Saida em lote",
            subtitulo: "Informe quanto saiu para cada medicamento selecionado.",
            quantidadeLabel: "Quantidade que saiu",
            quantidadeMin: "1",
            quantidadeInicial: "1",
            origemLabel: "Destino",
            origemPlaceholder: "Paciente, setor, perda ou vencimento",
            botao: "Salvar saida",
            botaoClasse: "btn-danger"
        },
        AJUSTE: {
            titulo: "Ajuste de saldo em lote",
            subtitulo: "Informe o novo saldo final de cada medicamento selecionado.",
            quantidadeLabel: "Novo saldo",
            quantidadeMin: "0",
            quantidadeInicial: "",
            origemLabel: "Motivo do ajuste",
            origemPlaceholder: "Inventario ou correcao de saldo",
            botao: "Salvar ajuste",
            botaoClasse: "btn-warning"
        }
    };

    function medicamentosSelecionados() {
        return checkboxes.filter(function (checkbox) {
            return checkbox.checked;
        });
    }

    function atualizarEstadoSelecao() {
        const totalSelecionados = medicamentosSelecionados().length;
        const nenhumSelecionado = totalSelecionados === 0;

        contadorSelecionados.textContent = `${totalSelecionados} selecionado(s)`;

        botoesLote.forEach(function (botao) {
            botao.disabled = nenhumSelecionado;
        });

        if (selecionarTodos) {
            selecionarTodos.checked = totalSelecionados === checkboxes.length;
            selecionarTodos.indeterminate = totalSelecionados > 0 && totalSelecionados < checkboxes.length;
        }
    }

    function criarTexto(classe, texto) {
        const elemento = document.createElement("div");
        elemento.className = classe;
        elemento.textContent = texto;

        return elemento;
    }

    function criarItemSelecionado(checkbox, tipo, config) {
        const medicamentoId = checkbox.dataset.medicamentoId;
        const estoqueAtual = Number(checkbox.dataset.estoqueAtual || "0");
        const unidade = checkbox.dataset.unidade || "unidade";
        const item = document.createElement("div");
        const info = document.createElement("div");
        const campo = document.createElement("div");
        const hidden = document.createElement("input");
        const label = document.createElement("label");
        const input = document.createElement("input");

        item.className = "bulk-item-row";
        info.appendChild(criarTexto("bulk-item-name", checkbox.dataset.medicamentoNome || "Medicamento"));
        info.appendChild(criarTexto("bulk-item-meta", `Estoque atual: ${estoqueAtual} ${unidade}`));

        hidden.type = "hidden";
        hidden.name = "medicamentos";
        hidden.value = medicamentoId;

        label.setAttribute("for", `quantidade-lote-${medicamentoId}`);
        label.textContent = config.quantidadeLabel;

        input.type = "number";
        input.className = "form-control";
        input.id = `quantidade-lote-${medicamentoId}`;
        input.name = `quantidade_${medicamentoId}`;
        input.min = config.quantidadeMin;
        input.step = "1";
        input.required = true;

        if (tipo === "SAIDA") {
            input.max = String(estoqueAtual);
        }

        if (tipo === "AJUSTE") {
            input.value = String(estoqueAtual);
        } else {
            input.value = config.quantidadeInicial;
        }

        campo.appendChild(label);
        campo.appendChild(input);
        item.appendChild(hidden);
        item.appendChild(info);
        item.appendChild(campo);

        return item;
    }

    function limparClasseBotaoConfirmar() {
        botaoConfirmar.classList.remove("btn-primary", "btn-success", "btn-danger", "btn-warning");
    }

    function abrirModalMovimentacao(tipo) {
        const selecionados = medicamentosSelecionados();
        const config = configuracoesTipo[tipo];

        if (!selecionados.length || !config) {
            return;
        }

        tipoMovimentacaoInput.value = tipo;
        tituloModal.textContent = config.titulo;
        subtituloModal.textContent = config.subtitulo;
        resumoItens.textContent = `${selecionados.length} item(ns)`;
        labelOrigemDestino.textContent = config.origemLabel;
        origemDestinoInput.placeholder = config.origemPlaceholder;
        botaoConfirmar.textContent = config.botao;
        limparClasseBotaoConfirmar();
        botaoConfirmar.classList.add(config.botaoClasse);
        itensContainer.replaceChildren();

        selecionados.forEach(function (checkbox) {
            itensContainer.appendChild(criarItemSelecionado(checkbox, tipo, config));
        });

        modalLote.show();
    }

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", atualizarEstadoSelecao);
    });

    if (selecionarTodos) {
        selecionarTodos.addEventListener("change", function () {
            checkboxes.forEach(function (checkbox) {
                checkbox.checked = selecionarTodos.checked;
            });

            atualizarEstadoSelecao();
        });
    }

    botoesLote.forEach(function (botao) {
        botao.addEventListener("click", function () {
            abrirModalMovimentacao(botao.dataset.bulkAction);
        });
    });

    atualizarEstadoSelecao();
});
