(function () {
    const config = window.tecnologiaAutoStatus;

    if (!config || !config.url) {
        return;
    }

    const statusClasses = ["online", "offline", "desconhecido"];
    let inFlight = false;

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);

        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }

        return "";
    }

    function updateMetric(name, value) {
        const element = document.querySelector(`[data-metric="${name}"]`);

        if (element) {
            element.textContent = value;
        }
    }

    function replaceStatusClass(element, nextClass) {
        if (!element) {
            return;
        }

        statusClasses.forEach((className) => element.classList.remove(className));
        element.classList.add(nextClass);
    }

    function updateEquipment(item) {
        const card = document.querySelector(`[data-equipment-id="${item.id}"]`);

        if (!card) {
            return;
        }

        replaceStatusClass(card, item.status_class);
        replaceStatusClass(card.querySelector(".status-dot"), item.status_class);

        const label = card.querySelector('[data-role="status-label"]');
        replaceStatusClass(label, item.status_class);

        if (label) {
            label.textContent = item.status_label;
        }

        const lastCheck = card.querySelector('[data-role="last-check"]');

        if (lastCheck) {
            lastCheck.textContent = item.ultima_verificacao;
        }

        const name = card.querySelector('[data-role="equipment-name"]');

        if (name && item.nome) {
            name.textContent = item.nome;
        }

        const macLine = card.querySelector('[data-role="mac-line"]');
        const macValue = card.querySelector('[data-role="mac-value"]');

        if (macLine && macValue && item.mac_address) {
            macValue.textContent = item.mac_address;
            macLine.hidden = false;
        }
    }

    async function refreshStatus() {
        if (inFlight || document.hidden) {
            return;
        }

        const cards = Array.from(document.querySelectorAll("[data-equipment-id]"));

        if (!cards.length) {
            return;
        }

        inFlight = true;

        try {
            const response = await fetch(config.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    ids: cards.map((card) => card.dataset.equipmentId)
                })
            });

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            (data.equipamentos || []).forEach(updateEquipment);

            if (data.totais) {
                updateMetric("total", data.totais.total);
                updateMetric("online", data.totais.online);
                updateMetric("offline", data.totais.offline);
                updateMetric("desconhecidos", data.totais.desconhecidos);
            }
        } catch (error) {
            return;
        } finally {
            inFlight = false;
        }
    }

    window.setTimeout(refreshStatus, 5000);
    window.setInterval(refreshStatus, config.intervalMs || 30000);
})();
