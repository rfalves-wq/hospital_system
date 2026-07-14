document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formRecepcao");
    const botaoSalvar = document.getElementById("btnSalvarClassificacao");
    const alertaEnvio = document.getElementById("alertaEnvioClassificacao");

    const cepInput = document.getElementById("id_cep");
    const municipioInput = document.getElementById("id_municipio");
    const bairroInput = document.getElementById("id_bairro");
    const logradouroInput = document.getElementById("id_logradouro");

    const cpfInput = document.getElementById("id_cpf");
    const cpfResponsavelInput = document.getElementById("id_cpf_responsavel");
    const cnsInput = document.getElementById("id_cns");
    const telefoneInput = document.getElementById("id_telefone");
    const emailInput = document.getElementById("id_email");
    const nascimentoInput = document.getElementById("id_nascimento");
    const idadeInput = document.getElementById("id_idade");

    const nomeResponsavelInput = document.getElementById("id_nome_responsavel");
    const secaoResponsavel = document.getElementById("secao-responsavel");
    const responsavelBadge = document.getElementById("responsavelObrigatorioBadge");
    const alertaResponsavelMenor = document.getElementById("alertaResponsavelMenor");
    const requiredMinorMarks = document.querySelectorAll(".required-minor");
    const faixaEtariaBadge = document.getElementById("faixaEtariaBadge");
    const faixaEtariaTexto = document.getElementById("faixaEtariaTexto");
    const idadeResumo = document.getElementById("idadeResumo");

    const nacionalidadeInput = document.getElementById("id_nacionalidade");
    const campoUfNascimento = document.getElementById("campo-uf-nascimento");
    const campoNaturalidade = document.getElementById("campo-naturalidade");
    const ufNascimentoInput = document.getElementById("id_uf_nascimento");
    const naturalidadeInput = document.getElementById("id_naturalidade");

    const ufNascimentoResponsavelInput = document.getElementById("id_uf_nascimento_responsavel");
    const naturalidadeResponsavelInput = document.getElementById("id_naturalidade_responsavel");

    let ultimoCepBuscado = "";

    function limparNumeros(valor) {
        return String(valor || "").replace(/\D/g, "");
    }

    function preencherCampo(campo, valor) {
        if (campo && valor) {
            campo.value = valor;
        }
    }

    function formatarCpf(valor) {
        const cpf = limparNumeros(valor).slice(0, 11);

        return cpf
            .replace(/^(\d{3})(\d)/, "$1.$2")
            .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
            .replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
    }

    function formatarCep(cep) {
        cep = limparNumeros(cep);

        if (cep.length > 5) {
            return cep.slice(0, 5) + "-" + cep.slice(5, 8);
        }

        return cep;
    }

    function formatarTelefone(valor) {
        let telefone = limparNumeros(valor);

        if (telefone.length > 11) {
            telefone = telefone.slice(0, 11);
        }

        if (telefone.length <= 10) {
            telefone = telefone.replace(/^(\d{2})(\d)/, "($1) $2");
            telefone = telefone.replace(/(\d{4})(\d)/, "$1-$2");
        } else {
            telefone = telefone.replace(/^(\d{2})(\d)/, "($1) $2");
            telefone = telefone.replace(/(\d{5})(\d)/, "$1-$2");
        }

        return telefone;
    }

    function calcularIdade(dataNascimento) {
        if (!dataNascimento) {
            return null;
        }

        const nascimento = new Date(`${dataNascimento}T00:00:00`);

        if (Number.isNaN(nascimento.getTime())) {
            return null;
        }

        const hoje = new Date();
        let idade = hoje.getFullYear() - nascimento.getFullYear();
        const mes = hoje.getMonth() - nascimento.getMonth();

        if (mes < 0 || (mes === 0 && hoje.getDate() < nascimento.getDate())) {
            idade -= 1;
        }

        return idade >= 0 ? idade : null;
    }

    function idadeAtual() {
        const idade = Number.parseInt(idadeInput ? idadeInput.value : "", 10);
        return Number.isFinite(idade) ? idade : null;
    }

    function dadosResponsavelObrigatorios() {
        const idade = idadeAtual();
        return idade !== null && idade < 18;
    }

    function atualizarFaixaEtaria() {
        const idade = idadeAtual();
        let texto = "Adulto";
        let classe = "adulto";

        if (idade === null) {
            texto = "-";
            classe = "";
        } else if (idade < 13) {
            texto = "Criança";
            classe = "crianca";
        } else if (idade < 18) {
            texto = "Adolescente";
            classe = "adolescente";
        }

        if (idadeResumo && idade !== null) {
            idadeResumo.textContent = String(idade);
        }

        if (faixaEtariaTexto) {
            faixaEtariaTexto.textContent = texto;
        }

        if (faixaEtariaBadge) {
            faixaEtariaBadge.textContent = texto;
            faixaEtariaBadge.className = `faixa-badge ms-2 ${classe}`;
        }

        const menor = dadosResponsavelObrigatorios();

        if (nomeResponsavelInput) {
            nomeResponsavelInput.required = menor;
        }

        if (cpfResponsavelInput) {
            cpfResponsavelInput.required = menor;
        }

        if (responsavelBadge) {
            responsavelBadge.classList.toggle("d-none", !menor);
        }

        if (alertaResponsavelMenor) {
            alertaResponsavelMenor.classList.toggle("d-none", !menor);
        }

        if (secaoResponsavel) {
            secaoResponsavel.classList.toggle("precisa-responsavel", menor);
        }

        requiredMinorMarks.forEach(function (marca) {
            marca.classList.toggle("d-none", !menor);
        });
    }

    function mostrarErroCep(mensagem) {
        let erro = document.getElementById("erro-cep");

        if (!erro && cepInput) {
            erro = document.createElement("div");
            erro.id = "erro-cep";
            erro.className = "text-danger small mt-1";
            cepInput.insertAdjacentElement("afterend", erro);
        }

        if (erro) {
            erro.textContent = mensagem;
        }
    }

    function limparErroCep() {
        const erro = document.getElementById("erro-cep");

        if (erro) {
            erro.textContent = "";
        }
    }

    async function buscarCep() {
        if (!cepInput) {
            return;
        }

        const cep = limparNumeros(cepInput.value);

        if (cep.length !== 8) {
            ultimoCepBuscado = "";
            limparErroCep();
            return;
        }

        if (cep === ultimoCepBuscado) {
            return;
        }

        ultimoCepBuscado = cep;
        limparErroCep();

        try {
            const resposta = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const dados = await resposta.json();

            if (dados.erro) {
                mostrarErroCep("CEP não encontrado.");
                return;
            }

            preencherCampo(municipioInput, dados.localidade);
            preencherCampo(bairroInput, dados.bairro);
            preencherCampo(logradouroInput, dados.logradouro);
        } catch (erro) {
            mostrarErroCep("Não foi possível buscar o CEP agora.");
        }
    }

    function mostrarErroEmail(mensagem) {
        let erro = document.getElementById("erro-email");

        if (!erro && emailInput) {
            erro = document.createElement("div");
            erro.id = "erro-email";
            erro.className = "text-danger small mt-1";
            emailInput.insertAdjacentElement("afterend", erro);
        }

        if (erro) {
            erro.textContent = mensagem;
        }
    }

    function limparErroEmail() {
        const erro = document.getElementById("erro-email");

        if (erro) {
            erro.textContent = "";
        }
    }

    function validarEmail() {
        if (!emailInput) {
            return;
        }

        emailInput.value = emailInput.value.trim().toLowerCase().replace(/\s/g, "");

        if (!emailInput.value) {
            limparErroEmail();
            return;
        }

        const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value);

        if (!emailValido) {
            mostrarErroEmail("E-mail inválido.");
        } else {
            limparErroEmail();
        }
    }

    function obterListaNaturalidades(naturalidadeInput) {
        const listaId = naturalidadeInput.getAttribute("list");

        if (!listaId) {
            return null;
        }

        return document.getElementById(listaId);
    }

    function limparSugestoesNaturalidade(naturalidadeInput, placeholder) {
        const lista = obterListaNaturalidades(naturalidadeInput);

        if (lista) {
            lista.innerHTML = "";
        }

        naturalidadeInput.placeholder = placeholder;
    }

    function preencherSugestoesNaturalidade(naturalidadeInput, cidades) {
        const lista = obterListaNaturalidades(naturalidadeInput);

        if (!lista) {
            return;
        }

        lista.innerHTML = "";

        cidades.forEach(function (cidade) {
            if (!cidade.nome) {
                return;
            }

            const option = document.createElement("option");
            option.value = cidade.nome;
            lista.appendChild(option);
        });
    }

    async function buscarCidadesPorUf(uf) {
        const urls = [
            `/recepcao/api/cidades/${encodeURIComponent(uf)}/`,
            `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${encodeURIComponent(uf)}/municipios`
        ];

        for (const url of urls) {
            try {
                const resposta = await fetch(
                    url,
                    {
                        headers: {
                            "Accept": "application/json"
                        }
                    }
                );

                if (!resposta.ok) {
                    continue;
                }

                const cidades = await resposta.json();

                if (Array.isArray(cidades)) {
                    return cidades;
                }
            } catch (erro) {
                continue;
            }
        }

        throw new Error("Falha ao carregar cidades.");
    }

    async function carregarNaturalidadesPorUf(ufInput, naturalidadeInput) {
        if (!ufInput || !naturalidadeInput) {
            return;
        }

        const uf = ufInput.value;
        const valorAtual = naturalidadeInput.dataset.valorAtual || naturalidadeInput.value || "";

        limparSugestoesNaturalidade(
            naturalidadeInput,
            "Selecione a UF ou digite a cidade"
        );

        if (!uf) {
            return;
        }

        naturalidadeInput.placeholder = "Carregando cidades...";

        try {
            const cidades = await buscarCidadesPorUf(uf);
            preencherSugestoesNaturalidade(naturalidadeInput, cidades);
            naturalidadeInput.placeholder = "Digite ou selecione a naturalidade";

            if (valorAtual && !naturalidadeInput.value) {
                naturalidadeInput.value = valorAtual;
            }
        } catch (erro) {
            limparSugestoesNaturalidade(
                naturalidadeInput,
                "Nao foi possivel carregar. Digite a cidade"
            );
        }
    }

    function controlarCamposNascimento() {
        if (
            !nacionalidadeInput ||
            !campoUfNascimento ||
            !campoNaturalidade ||
            !ufNascimentoInput ||
            !naturalidadeInput
        ) {
            return;
        }

        const nacionalidade = nacionalidadeInput.value.toLowerCase();

        if (nacionalidade === "brasileira") {
            campoUfNascimento.classList.remove("d-none");
            campoNaturalidade.classList.remove("d-none");

            ufNascimentoInput.required = true;
            naturalidadeInput.required = true;

            carregarNaturalidadesPorUf(ufNascimentoInput, naturalidadeInput);
        } else {
            campoUfNascimento.classList.add("d-none");
            campoNaturalidade.classList.add("d-none");

            ufNascimentoInput.required = false;
            naturalidadeInput.required = false;

            ufNascimentoInput.value = "";
            limparSugestoesNaturalidade(
                naturalidadeInput,
                "Selecione a UF ou digite a cidade"
            );
            naturalidadeInput.value = "";
        }
    }

    function focarSecaoResponsavel() {
        if (!secaoResponsavel) {
            return;
        }

        secaoResponsavel.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    function focarCampoOuSecao(campo) {
        if (!campo) {
            return;
        }

        const secao = campo.closest(".form-section");

        if (!secao) {
            return;
        }

        secao.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    function primeiroCampoInvalido() {
        if (!form) {
            return null;
        }

        return Array.from(
            form.querySelectorAll("input, select, textarea")
        ).find(function (campo) {
            return !campo.disabled && !campo.checkValidity();
        }) || null;
    }

    if (cepInput) {
        cepInput.addEventListener("input", function () {
            cepInput.value = formatarCep(cepInput.value);
            buscarCep();
        });

        cepInput.addEventListener("blur", buscarCep);
    }

    if (cpfInput) {
        cpfInput.addEventListener("input", function () {
            cpfInput.value = formatarCpf(cpfInput.value);
        });
    }

    if (cpfResponsavelInput) {
        cpfResponsavelInput.addEventListener("input", function () {
            cpfResponsavelInput.value = formatarCpf(cpfResponsavelInput.value);
        });
    }

    if (cnsInput) {
        cnsInput.addEventListener("input", function () {
            let cns = limparNumeros(cnsInput.value);

            if (cns.length > 15) {
                cns = cns.slice(0, 15);
            }

            cns = cns.replace(/^(\d{3})(\d)/, "$1 $2");
            cns = cns.replace(/^(\d{3})\s(\d{4})(\d)/, "$1 $2 $3");
            cns = cns.replace(/^(\d{3})\s(\d{4})\s(\d{4})(\d)/, "$1 $2 $3 $4");

            cnsInput.value = cns;
        });
    }

    if (telefoneInput) {
        telefoneInput.addEventListener("input", function () {
            telefoneInput.value = formatarTelefone(telefoneInput.value);
        });
    }

    if (emailInput) {
        emailInput.addEventListener("input", function () {
            emailInput.value = emailInput.value.toLowerCase().replace(/\s/g, "");
        });

        emailInput.addEventListener("blur", validarEmail);
    }

    if (nascimentoInput && idadeInput) {
        nascimentoInput.addEventListener("change", function () {
            const idadeCalculada = calcularIdade(nascimentoInput.value);

            if (idadeCalculada !== null) {
                idadeInput.value = idadeCalculada;
            }

            atualizarFaixaEtaria();
        });
    }

    if (idadeInput) {
        idadeInput.addEventListener("input", atualizarFaixaEtaria);
        atualizarFaixaEtaria();
    }

    if (nacionalidadeInput) {
        nacionalidadeInput.addEventListener("change", controlarCamposNascimento);
        controlarCamposNascimento();
    }

    if (ufNascimentoInput) {
        ufNascimentoInput.addEventListener("change", function () {
            if (naturalidadeInput) {
                naturalidadeInput.dataset.valorAtual = "";
                naturalidadeInput.value = "";
            }

            carregarNaturalidadesPorUf(ufNascimentoInput, naturalidadeInput);
        });
    }

    if (ufNascimentoResponsavelInput) {
        carregarNaturalidadesPorUf(ufNascimentoResponsavelInput, naturalidadeResponsavelInput);

        ufNascimentoResponsavelInput.addEventListener("change", function () {
            if (naturalidadeResponsavelInput) {
                naturalidadeResponsavelInput.dataset.valorAtual = "";
                naturalidadeResponsavelInput.value = "";
            }

            carregarNaturalidadesPorUf(
                ufNascimentoResponsavelInput,
                naturalidadeResponsavelInput
            );
        });
    }

    const primeiroErro = document.querySelector(".form-section .errorlist");

    if (primeiroErro) {
        focarCampoOuSecao(primeiroErro);
    }

    if (form) {
        form.addEventListener("submit", function (evento) {
            atualizarFaixaEtaria();

            if (
                dadosResponsavelObrigatorios() &&
                (
                    !nomeResponsavelInput ||
                    !cpfResponsavelInput ||
                    !nomeResponsavelInput.value.trim() ||
                    !cpfResponsavelInput.value.trim()
                )
            ) {
                evento.preventDefault();
                focarSecaoResponsavel();
                alert("Paciente menor de 18 anos. Preencha o nome e CPF do responsável.");

                if (nomeResponsavelInput && !nomeResponsavelInput.value.trim()) {
                    nomeResponsavelInput.focus();
                } else if (cpfResponsavelInput) {
                    cpfResponsavelInput.focus();
                }

                return;
            }

            const campoInvalido = primeiroCampoInvalido();

            if (campoInvalido) {
                evento.preventDefault();
                focarCampoOuSecao(campoInvalido);

                setTimeout(function () {
                    campoInvalido.focus();
                    campoInvalido.reportValidity();
                }, 150);

                return;
            }

            const confirmar = confirm(
                "Salvar cadastro e encaminhar o paciente para a Classificação de Risco?"
            );

            if (!confirmar) {
                evento.preventDefault();
                return;
            }

            if (alertaEnvio) {
                alertaEnvio.classList.remove("d-none");
            }

            alert("Cadastro confirmado. O paciente será encaminhado para a fila da Classificação de Risco.");

            if (botaoSalvar) {
                botaoSalvar.disabled = true;

                const texto = botaoSalvar.querySelector(".btn-text");
                const loading = botaoSalvar.querySelector(".btn-loading");

                if (texto && loading) {
                    texto.classList.add("d-none");
                    loading.classList.remove("d-none");
                }
            }
        });
    }

    const camposFormulario = Array.from(
        document.querySelectorAll("input, select, textarea, button")
    ).filter(function (campo) {
        return !campo.disabled && campo.type !== "hidden";
    });

    camposFormulario.forEach(function (campo, indice) {
        campo.addEventListener("keydown", function (evento) {
            if (evento.key !== "Enter") {
                return;
            }

            if (campo.tagName === "TEXTAREA") {
                return;
            }

            evento.preventDefault();

            const proximoCampo = camposFormulario[indice + 1];

            if (proximoCampo) {
                proximoCampo.focus();
            } else if (campo.form) {
                campo.form.requestSubmit();
            }
        });
    });
});
