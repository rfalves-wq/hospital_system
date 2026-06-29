document.addEventListener("DOMContentLoaded", function () {
    const cepInput = document.getElementById("id_cep");
    const municipioInput = document.getElementById("id_municipio");
    const bairroInput = document.getElementById("id_bairro");
    const logradouroInput = document.getElementById("id_logradouro");

    let ultimoCepBuscado = "";

    if (!cepInput) {
        return;
    }

    function limparCep(cep) {
        return cep.replace(/\D/g, "");
    }

    function formatarCep(cep) {
        cep = limparCep(cep);

        if (cep.length > 5) {
            return cep.slice(0, 5) + "-" + cep.slice(5, 8);
        }

        return cep;
    }

    function preencherCampo(campo, valor) {
        if (campo && valor) {
            campo.value = valor;
        }
    }

    function mostrarErroCep(mensagem) {
        let erro = document.getElementById("erro-cep");

        if (!erro) {
            erro = document.createElement("div");
            erro.id = "erro-cep";
            erro.className = "text-danger small mt-1";
            cepInput.insertAdjacentElement("afterend", erro);
        }

        erro.textContent = mensagem;
    }

    function limparErroCep() {
        const erro = document.getElementById("erro-cep");

        if (erro) {
            erro.textContent = "";
        }
    }

    async function buscarCep() {
        const cep = limparCep(cepInput.value);

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

    cepInput.addEventListener("input", function () {
        cepInput.value = formatarCep(cepInput.value);
        buscarCep();
    });

    cepInput.addEventListener("blur", buscarCep);
});

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
        } else {
            campo.form.submit();
        }
    });
});



const telefoneInput = document.getElementById("id_telefone");

if (telefoneInput) {
    telefoneInput.addEventListener("input", function () {
        let telefone = telefoneInput.value.replace(/\D/g, "");

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

const emailInput = document.getElementById("id_email");

if (emailInput) {
    function mostrarErroEmail(mensagem) {
        let erro = document.getElementById("erro-email");

        if (!erro) {
            erro = document.createElement("div");
            erro.id = "erro-email";
            erro.className = "text-danger small mt-1";
            emailInput.insertAdjacentElement("afterend", erro);
        }

        erro.textContent = mensagem;
    }

    function limparErroEmail() {
        const erro = document.getElementById("erro-email");

        if (erro) {
            erro.textContent = "";
        }
    }

    function validarEmail() {
        const email = emailInput.value.trim().toLowerCase();
        emailInput.value = email.replace(/\s/g, "");

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

    emailInput.addEventListener("input", function () {
        emailInput.value = emailInput.value.toLowerCase().replace(/\s/g, "");
    });

    emailInput.addEventListener("blur", validarEmail);
}

const nacionalidadeInput = document.getElementById("id_nacionalidade");
const campoUfNascimento = document.getElementById("campo-uf-nascimento");
const campoNaturalidade = document.getElementById("campo-naturalidade");
const ufNascimentoInput = document.getElementById("id_uf_nascimento");
const naturalidadeInput = document.getElementById("id_naturalidade");

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
    } else {
        campoUfNascimento.classList.add("d-none");
        campoNaturalidade.classList.add("d-none");

        ufNascimentoInput.required = false;
        naturalidadeInput.required = false;

        ufNascimentoInput.value = "";
        naturalidadeInput.value = "";
    }
}

if (nacionalidadeInput) {
    nacionalidadeInput.addEventListener("change", controlarCamposNascimento);
    controlarCamposNascimento();
}