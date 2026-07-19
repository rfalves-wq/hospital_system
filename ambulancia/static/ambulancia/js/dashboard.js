(function () {
    const selectPaciente = document.getElementById("id_acolhimento");
    const dadosEl = document.getElementById("pacientes-ambulancia-data");

    if (selectPaciente && dadosEl) {
        let pacientes = {};

        try {
            pacientes = JSON.parse(dadosEl.textContent || "{}");
        } catch (error) {
            pacientes = {};
        }

        selectPaciente.addEventListener("change", function () {
            const paciente = pacientes[this.value];

            if (!paciente) {
                return;
            }

            preencherCampo("id_nome_paciente", paciente.nome);
            preencherCampo("id_numero_bam", paciente.bam);
            preencherCampo("id_cpf", paciente.cpf);
            preencherCampo("id_data_nascimento", paciente.nascimento);
            preencherCampo("id_origem", paciente.origem || "Hospital");
        });
    }

    document.querySelectorAll(".status-action-form").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const status = form.querySelector("input[name='status']");

            if (status && status.value === "CANCELADO") {
                const confirmado = window.confirm("Cancelar esta solicitacao de ambulancia?");

                if (!confirmado) {
                    event.preventDefault();
                }
            }
        });
    });

    document.querySelectorAll(".trip-open-button").forEach(function (button) {
        button.addEventListener("click", function () {
            const dialogId = button.dataset.dialogTarget;
            const dialog = document.getElementById(dialogId);

            if (!dialog) {
                return;
            }

            try {
                if (typeof dialog.showModal === "function") {
                    dialog.showModal();
                } else {
                    dialog.setAttribute("open", "open");
                }
            } catch (error) {
                dialog.setAttribute("open", "open");
            }
        });
    });

    document.querySelectorAll(".trip-dialog").forEach(function (dialog) {
        dialog.querySelectorAll(".trip-close-button, .trip-cancel-button").forEach(function (button) {
            button.addEventListener("click", function () {
                dialog.close();
            });
        });

        dialog.addEventListener("click", function (event) {
            if (event.target === dialog) {
                dialog.close();
            }
        });
    });

    function preencherCampo(id, valor) {
        const campo = document.getElementById(id);

        if (!campo || !valor) {
            return;
        }

        campo.value = valor;
    }
}());
