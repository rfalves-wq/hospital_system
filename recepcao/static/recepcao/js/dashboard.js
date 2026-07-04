/* =========================
   ABRIR REGISTRO + PREENCHER
========================= */
document.addEventListener('click', function (e) {

    const el = e.target.closest('.paciente-link');
    if (!el) return;

    e.preventDefault();

    const set = (id, val) => {
        const input = document.getElementById(id);
        if (input) input.value = val || '';
    };

    set('nome_completo', el.dataset.nome);
    set('cpf', el.dataset.cpf);
    set('data_nascimento', el.dataset.nascimento);

    const tab = document.querySelector('button[data-bs-target="#registro"]');
    if (tab) new bootstrap.Tab(tab).show();
});


/* =========================
   ENTER → PRÓXIMO CAMPO
========================= */
document.addEventListener('keydown', function (e) {

    if (e.key !== 'Enter') return;

    const el = e.target;
    const form = el.closest('form');
    if (!form) return;

    if (el.tagName === 'TEXTAREA') return;

    e.preventDefault();

    const fields = [...form.querySelectorAll('input, select, textarea')]
        .filter(f =>
            !f.disabled &&
            !f.readOnly &&
            f.type !== 'hidden' &&
            f.offsetParent !== null
        );

    const i = fields.indexOf(el);

    if (i > -1 && i < fields.length - 1) {
        fields[i + 1].focus();
        fields[i + 1].select?.();
    }
});


/* =========================
   CPF MÁSCARA
========================= */
document.addEventListener('input', function (e) {

    if (e.target.id !== 'cpf') return;

    let v = e.target.value.replace(/\D/g, '').slice(0, 11);

    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');

    e.target.value = v;
});


/* =========================
   IDADE (VERSÃO ÚNICA CORRETA)
========================= */
function calcularIdadeAuto() {

    const data = document.getElementById('data_nascimento');
    const idade = document.getElementById('idade');
    const resp = document.getElementById('responsavel_container');

    if (!data || !idade) return;

    if (!data.value) {
        idade.value = '';
        if (resp) resp.style.display = 'none';
        return;
    }

    const nasc = new Date(data.value);
    const hoje = new Date();

    let i = hoje.getFullYear() - nasc.getFullYear();
    const m = hoje.getMonth() - nasc.getMonth();

    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) i--;

    idade.value = i;

    if (resp) {
        resp.style.display = i < 18 ? 'flex' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('data_nascimento');
    if (el) el.addEventListener('change', calcularIdadeAuto);
});


/* =========================
   NATURALIDADE (IBGE)
========================= */
document.addEventListener('DOMContentLoaded', () => {

    const uf = document.getElementById('uf_naturalidade');
    const cidade = document.getElementById('naturalidade');

    if (!uf || !cidade) return;

    uf.addEventListener('change', function () {

        cidade.innerHTML = '<option>Carregando...</option>';

        fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${this.value}/municipios`)
            .then(r => r.json())
            .then(data => {

                cidade.innerHTML = '<option value="">Selecione</option>';

                data.forEach(c => {
                    cidade.innerHTML += `<option value="${c.nome}">${c.nome}</option>`;
                });

            });

    });
});


/* =========================
   CEP (VIACEP)
========================= */
document.addEventListener('DOMContentLoaded', () => {

    const cep = document.getElementById('cep');
    const municipio = document.getElementById('municipio');

    if (!cep || !municipio) return;

    cep.addEventListener('blur', function () {

        let v = this.value.replace(/\D/g, '');

        if (v.length !== 8) return;

        fetch(`https://viacep.com.br/ws/${v}/json/`)
            .then(r => r.json())
            .then(d => {

                if (d.erro) return;

                municipio.value = d.localidade || '';

            });
    });

    cep.addEventListener('input', function () {

        let v = this.value.replace(/\D/g, '').slice(0, 8);

        if (v.length > 5) v = v.replace(/^(\d{5})(\d)/, '$1-$2');

        this.value = v;
    });
});


/* =========================
   TELEFONE
========================= */
document.addEventListener('input', function (e) {

    if (e.target.id !== 'telefone') return;

    let v = e.target.value.replace(/\D/g, '').slice(0, 11);

    if (v.length <= 10) {
        v = v.replace(/(\d{2})(\d)/, '($1) $2');
        v = v.replace(/(\d{4})(\d)/, '$1-$2');
    } else {
        v = v.replace(/(\d{2})(\d)/, '($1) $2');
        v = v.replace(/(\d{5})(\d)/, '$1-$2');
    }

    e.target.value = v;
});


/* =========================
   EMAIL VALIDAÇÃO
========================= */
document.addEventListener('input', function (e) {

    if (e.target.id !== 'email') return;

    if (e.target.checkValidity()) {
        e.target.classList.add('is-valid');
        e.target.classList.remove('is-invalid');
    } else {
        e.target.classList.add('is-invalid');
        e.target.classList.remove('is-valid');
    }
});

 document.addEventListener("DOMContentLoaded", function () {
    const botoesAbas = document.querySelectorAll('[data-bs-toggle="tab"]');
    const abaSalva = localStorage.getItem("abaRecepcaoAtiva");

    if (abaSalva) {
        const botaoAba = document.querySelector(`[data-bs-target="${abaSalva}"]`);

        if (botaoAba && window.bootstrap) {
            const aba = new bootstrap.Tab(botaoAba);
            aba.show();
        }
    }

    botoesAbas.forEach(function (botao) {
        botao.addEventListener("shown.bs.tab", function (evento) {
            const destino = evento.target.getAttribute("data-bs-target");
            localStorage.setItem("abaRecepcaoAtiva", destino);
        });
    });

    setInterval(function () {
        const abaAtiva = localStorage.getItem("abaRecepcaoAtiva");

        if (abaAtiva !== "#historico") {
            window.location.reload();
        }
    }, 10000);
});