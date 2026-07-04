document.addEventListener("DOMContentLoaded", function () {
    const cepInput = document.getElementById("id_cep");
    const municipioInput = document.getElementById("id_municipio");
    const bairroInput = document.getElementById("id_bairro");
    const logradouroInput = document.getElementById("id_logradouro");

    const telefoneInput = document.getElementById("id_telefone");
    const emailInput = document.getElementById("id_email");

    const nacionalidadeInput = document.getElementById("id_nacionalidade");
    const campoUfNascimento = document.getElementById("campo-uf-nascimento");
    const campoNaturalidade = document.getElementById("campo-naturalidade");
    const ufNascimentoInput = document.getElementById("id_uf_nascimento");
    const naturalidadeInput = document.getElementById("id_naturalidade");

    let ultimoCepBuscado = "";

    function limparNumeros(valor) {
        return valor.replace(/\D/g, "");
    }

    function preencherCampo(campo, valor) {
        if (campo && valor) {
            campo.value = valor;
        }
    }

    function formatarCep(cep) {
        cep = limparNumeros(cep);

        if (cep.length > 5) {
            return cep.slice(0, 5) + "-" + cep.slice(5, 8);
        }

        return cep;
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

    if (cepInput) {
        cepInput.addEventListener("input", function () {
            cepInput.value = formatarCep(cepInput.value);
            buscarCep();
        });

        cepInput.addEventListener("blur", buscarCep);
    }

    if (telefoneInput) {
        telefoneInput.addEventListener("input", function () {
            let telefone = limparNumeros(telefoneInput.value);

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

            telefoneInput.value = telefone;
        });
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

    if (emailInput) {
        emailInput.addEventListener("input", function () {
            emailInput.value = emailInput.value.toLowerCase().replace(/\s/g, "");
        });

        emailInput.addEventListener("blur", validarEmail);
    }

    async function carregarNaturalidades() {
        if (!ufNascimentoInput || !naturalidadeInput) {
            return;
        }

        const uf = ufNascimentoInput.value;
        const valorAtual = naturalidadeInput.dataset.valorAtual || "";

        naturalidadeInput.innerHTML = '<option value="">Selecione a UF primeiro</option>';

        if (!uf) {
            return;
        }

        naturalidadeInput.innerHTML = '<option value="">Carregando cidades...</option>';

        try {
            const resposta = await fetch(
                `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`
            );

            const cidades = await resposta.json();

            naturalidadeInput.innerHTML = '<option value="">Selecione a naturalidade</option>';

            cidades.forEach(function (cidade) {
                const option = document.createElement("option");
                option.value = cidade.nome;
                option.textContent = cidade.nome;

                if (cidade.nome === valorAtual) {
                    option.selected = true;
                }

                naturalidadeInput.appendChild(option);
            });

        } catch (erro) {
            naturalidadeInput.innerHTML = '<option value="">Erro ao carregar cidades</option>';
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

            carregarNaturalidades();
        } else {
            campoUfNascimento.classList.add("d-none");
            campoNaturalidade.classList.add("d-none");

            ufNascimentoInput.required = false;
            naturalidadeInput.required = false;

            ufNascimentoInput.value = "";
            naturalidadeInput.innerHTML = '<option value="">Selecione a UF primeiro</option>';
            naturalidadeInput.value = "";
        }
    }

    if (nacionalidadeInput) {
        nacionalidadeInput.addEventListener("change", controlarCamposNascimento);
        controlarCamposNascimento();
    }

    if (ufNascimentoInput) {
        ufNascimentoInput.addEventListener("change", function () {
            if (naturalidadeInput) {
                naturalidadeInput.dataset.valorAtual = "";
            }

            carregarNaturalidades();
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
                campo.form.submit();
            }
        });
    });
});

const cnsInput = document.getElementById("id_cns");

if (cnsInput) {
    cnsInput.addEventListener("input", function () {
        let cns = cnsInput.value.replace(/\D/g, "");

        if (cns.length > 15) {
            cns = cns.slice(0, 15);
        }

        cns = cns.replace(/^(\d{3})(\d)/, "$1 $2");
        cns = cns.replace(/^(\d{3})\s(\d{4})(\d)/, "$1 $2 $3");
        cns = cns.replace(/^(\d{3})\s(\d{4})\s(\d{4})(\d)/, "$1 $2 $3 $4");

        cnsInput.value = cns;
    });
}