document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-history-back]").forEach(function (botao) {
            botao.addEventListener("click", function () {
                history.back();
            });
        });

        const dataChegada = document.getElementById("id_data_chegada");
        const horaChegada = document.getElementById("id_hora_chegada");
        const agora = new Date();

        if (dataChegada && !dataChegada.value) {
            const ano = agora.getFullYear();
            const mes = String(agora.getMonth() + 1).padStart(2, "0");
            const dia = String(agora.getDate()).padStart(2, "0");
            dataChegada.value = `${ano}-${mes}-${dia}`;
        }

        if (horaChegada && !horaChegada.value) {
            const hora = String(agora.getHours()).padStart(2, "0");
            const minuto = String(agora.getMinutes()).padStart(2, "0");
            horaChegada.value = `${hora}:${minuto}`;
        }

        const radios = document.querySelectorAll('input[name="cor"]');
        const tempo = document.getElementById("tempoEspera");

        radios.forEach(function (radio) {
            radio.addEventListener("change", function () {
                if (this.value === "VERMELHO") tempo.innerHTML = "<strong class='text-danger'>Imediato</strong>";
                if (this.value === "LARANJA") tempo.innerHTML = "<strong class='texto-laranja'>10 minutos</strong>";
                if (this.value === "AMARELO") tempo.innerHTML = "<strong class='text-warning'>60 minutos</strong>";
                if (this.value === "VERDE") tempo.innerHTML = "<strong class='text-success'>120 minutos</strong>";
                if (this.value === "AZUL") tempo.innerHTML = "<strong class='text-primary'>240 minutos</strong>";
            });
        });
    });
