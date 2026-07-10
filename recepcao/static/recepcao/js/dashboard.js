/* =========================
   IMPRESSAO DA RECEPCAO
========================= */
function escaparHtml(valor) {
    return String(valor || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function textoOuTraco(valor) {
    if (valor === undefined || valor === null || valor === "") {
        return "-";
    }

    return String(valor);
}

function obterDadosImpressaoRecepcao() {
    const script = document.getElementById("dados-impressao-recepcao");

    if (!script) {
        return null;
    }

    try {
        return JSON.parse(script.textContent);
    } catch (erro) {
        return null;
    }
}

function imprimirDadosRecepcao(dados) {
    const ficha = dados || {};
    const agora = new Date();

    const campo = function (nome) {
        return textoOuTraco(ficha[nome]);
    };

    const conteudo = `
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <title>Ficha da Recepcao</title>
            <style>
                * {
                    box-sizing: border-box;
                }

                @page {
                    margin: 10mm;
                    size: A4;
                }

                body {
                    background: #fff;
                    color: #0f172a;
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 12px;
                    margin: 0;
                }

                .folha {
                    border: 1px solid #cbd5e1;
                    margin: 0 auto;
                    max-width: 780px;
                }

                .topo {
                    align-items: center;
                    background: #0f4c81;
                    color: #fff;
                    display: flex;
                    justify-content: space-between;
                    padding: 12px 14px;
                }

                .setor {
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: .08em;
                    text-transform: uppercase;
                }

                h1 {
                    font-size: 18px;
                    margin: 4px 0 0;
                }

                .badge {
                    background: #dcfce7;
                    border-radius: 999px;
                    color: #166534;
                    font-size: 12px;
                    font-weight: 900;
                    padding: 8px 12px;
                }

                .meta {
                    border-bottom: 1px solid #cbd5e1;
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                }

                .meta div {
                    border-right: 1px solid #cbd5e1;
                    padding: 7px 10px;
                }

                .meta div:last-child {
                    border-right: 0;
                }

                .secao {
                    padding: 12px 14px 0;
                }

                .secao-titulo {
                    border-bottom: 2px solid #0f4c81;
                    color: #0f4c81;
                    font-size: 13px;
                    font-weight: 900;
                    margin-bottom: 8px;
                    padding-bottom: 4px;
                    text-transform: uppercase;
                }

                table {
                    border-collapse: collapse;
                    margin-bottom: 10px;
                    width: 100%;
                }

                th,
                td {
                    border: 1px solid #cbd5e1;
                    padding: 7px 8px;
                    text-align: left;
                    vertical-align: top;
                }

                th {
                    background: #f1f5f9;
                    color: #334155;
                    font-size: 10px;
                    letter-spacing: .04em;
                    text-transform: uppercase;
                    width: 20%;
                }

                .valor-forte {
                    font-size: 14px;
                    font-weight: 900;
                    text-transform: uppercase;
                }

                .rodape {
                    display: grid;
                    gap: 22px;
                    grid-template-columns: 1fr 1fr;
                    padding: 24px 14px 14px;
                }

                .assinatura {
                    border-top: 1px solid #0f172a;
                    padding-top: 6px;
                    text-align: center;
                }

                .print-actions {
                    margin: 12px auto 0;
                    max-width: 780px;
                    text-align: right;
                }

                .print-actions button {
                    background: #0f4c81;
                    border: 0;
                    border-radius: 6px;
                    color: #fff;
                    cursor: pointer;
                    font-weight: 800;
                    padding: 9px 14px;
                }

                @media print {
                    .print-actions {
                        display: none;
                    }

                    .folha {
                        border-color: #111827;
                        max-width: none;
                    }

                    body {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                }
            </style>
        </head>
        <body>
            <div class="folha">
                <div class="topo">
                    <div>
                        <div class="setor">Recepcao</div>
                        <h1>Ficha de Cadastro Administrativo</h1>
                    </div>

                    <div class="badge">${escaparHtml(campo("status"))}</div>
                </div>

                <div class="meta">
                    <div>
                        <strong>BAM</strong><br>
                        <span>${escaparHtml(campo("numero_bam"))}</span>
                    </div>
                    <div>
                        <strong>Data da recepcao</strong><br>
                        <span>${escaparHtml(campo("data_recepcao"))}</span>
                    </div>
                    <div>
                        <strong>Hora chegada</strong><br>
                        <span>${escaparHtml(campo("hora_chegada"))}</span>
                    </div>
                    <div>
                        <strong>Impressao</strong><br>
                        <span>${escaparHtml(agora.toLocaleString("pt-BR"))}</span>
                    </div>
                </div>

                <div class="secao">
                    <div class="secao-titulo">Dados do paciente</div>
                    <table>
                        <tr>
                            <th>Paciente</th>
                            <td colspan="3" class="valor-forte">${escaparHtml(campo("nome_completo"))}</td>
                        </tr>
                        <tr>
                            <th>Nome social</th>
                            <td>${escaparHtml(campo("nome_social"))}</td>
                            <th>CPF</th>
                            <td>${escaparHtml(campo("cpf"))}</td>
                        </tr>
                        <tr>
                            <th>CNS</th>
                            <td>${escaparHtml(campo("cns"))}</td>
                            <th>Nascimento</th>
                            <td>${escaparHtml(campo("nascimento"))}</td>
                        </tr>
                        <tr>
                            <th>Idade</th>
                            <td>${escaparHtml(campo("idade"))} anos</td>
                            <th>Sexo</th>
                            <td>${escaparHtml(campo("sexo"))}</td>
                        </tr>
                        <tr>
                            <th>Raca/Cor</th>
                            <td>${escaparHtml(campo("raca_cor"))}</td>
                            <th>Situacao de rua</th>
                            <td>${escaparHtml(campo("situacao_rua"))}</td>
                        </tr>
                        <tr>
                            <th>Nacionalidade</th>
                            <td>${escaparHtml(campo("nacionalidade"))}</td>
                            <th>Naturalidade</th>
                            <td>${escaparHtml(campo("naturalidade"))} / ${escaparHtml(campo("uf_nascimento"))}</td>
                        </tr>
                    </table>
                </div>

                <div class="secao">
                    <div class="secao-titulo">Filiacao e contato</div>
                    <table>
                        <tr>
                            <th>Mae</th>
                            <td>${escaparHtml(campo("nome_mae"))}</td>
                            <th>Pai</th>
                            <td>${escaparHtml(campo("nome_pai"))}</td>
                        </tr>
                        <tr>
                            <th>Telefone</th>
                            <td>${escaparHtml(campo("telefone"))}</td>
                            <th>E-mail</th>
                            <td>${escaparHtml(campo("email"))}</td>
                        </tr>
                    </table>
                </div>

                <div class="secao">
                    <div class="secao-titulo">Endereco</div>
                    <table>
                        <tr>
                            <th>CEP</th>
                            <td>${escaparHtml(campo("cep"))}</td>
                            <th>Municipio</th>
                            <td>${escaparHtml(campo("municipio"))}</td>
                        </tr>
                        <tr>
                            <th>Bairro</th>
                            <td>${escaparHtml(campo("bairro"))}</td>
                            <th>Logradouro</th>
                            <td>${escaparHtml(campo("logradouro"))}</td>
                        </tr>
                        <tr>
                            <th>Numero</th>
                            <td>${escaparHtml(campo("numero"))}</td>
                            <th>Complemento</th>
                            <td>${escaparHtml(campo("complemento"))}</td>
                        </tr>
                    </table>
                </div>

                <div class="secao">
                    <div class="secao-titulo">Responsavel</div>
                    <table>
                        <tr>
                            <th>Nome</th>
                            <td>${escaparHtml(campo("nome_responsavel"))}</td>
                            <th>CPF</th>
                            <td>${escaparHtml(campo("cpf_responsavel"))}</td>
                        </tr>
                        <tr>
                            <th>Nacionalidade</th>
                            <td>${escaparHtml(campo("nacionalidade_responsavel"))}</td>
                            <th>Naturalidade</th>
                            <td>${escaparHtml(campo("naturalidade_responsavel"))} / ${escaparHtml(campo("uf_nascimento_responsavel"))}</td>
                        </tr>
                    </table>
                </div>

                <div class="rodape">
                    <div class="assinatura">Responsavel pela recepcao</div>
                    <div class="assinatura">Paciente / responsavel</div>
                </div>
            </div>

            <div class="print-actions">
                <button type="button" onclick="window.print()">Imprimir ficha</button>
            </div>
        </body>
        </html>
    `;

    const janela = window.open("", "_blank", "width=840,height=900");

    if (!janela) {
        alert("O navegador bloqueou a janela de impressao. Libere pop-ups para imprimir a ficha.");
        return;
    }

    janela.document.open();
    janela.document.write(conteudo);
    janela.document.close();
    janela.focus();

    setTimeout(function () {
        janela.print();
    }, 300);
}

document.addEventListener("DOMContentLoaded", function () {
    const dadosImpressao = obterDadosImpressaoRecepcao();
    const botaoImprimir = document.getElementById("btn-imprimir-recepcao");
    const modalElemento = document.getElementById("modal-impressao-recepcao");

    if (modalElemento && window.bootstrap) {
        const modal = new bootstrap.Modal(modalElemento);
        modal.show();

        modalElemento.addEventListener("hidden.bs.modal", function () {
            const script = document.getElementById("dados-impressao-recepcao");

            if (script) {
                script.remove();
            }
        });
    }

    if (botaoImprimir && dadosImpressao) {
        botaoImprimir.addEventListener("click", function () {
            imprimirDadosRecepcao(dadosImpressao);

            if (modalElemento && window.bootstrap) {
                bootstrap.Modal.getOrCreateInstance(modalElemento).hide();
            }
        });
    }
});


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
        if (document.getElementById("dados-impressao-recepcao")) {
            return;
        }

        const abaAtiva = localStorage.getItem("abaRecepcaoAtiva");

        if (abaAtiva !== "#historico") {
            window.location.reload();
        }
    }, 10000);
});
