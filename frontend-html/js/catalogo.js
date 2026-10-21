(function () {
    "use strict";

    var PLACEHOLDER_IMAGE = "./img/placeholder.svg";
    var CONDITION_LABELS = { new: "Novo", used: "Usado" };

    var priceFormatter = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
    var mileageFormatter = new Intl.NumberFormat("pt-BR");

    var states = {
        loading: document.getElementById("catalog-loading"),
        list: document.getElementById("catalog-list"),
        empty: document.getElementById("catalog-empty"),
        error: document.getElementById("catalog-error")
    };
    var retryButton = document.getElementById("catalog-retry");

    // Exibe somente um dos estados da página: loading, list, empty ou error.
    function showState(name) {
        Object.keys(states).forEach(function (key) {
            states[key].hidden = key !== name;
        });
    }

    function isHttpUrl(value) {
        if (typeof value !== "string" || value.trim() === "") {
            return false;
        }
        try {
            var url = new URL(value.trim());
            return url.protocol === "http:" || url.protocol === "https:";
        } catch (error) {
            return false;
        }
    }

    function vehicleTitle(vehicle) {
        return [vehicle.brand, vehicle.model, vehicle.version]
            .filter(function (part) {
                return typeof part === "string" && part.trim() !== "";
            })
            .map(function (part) {
                return part.trim();
            })
            .join(" ");
    }

    function usePlaceholder(image) {
        image.classList.add("is-placeholder");
        image.src = PLACEHOLDER_IMAGE;
    }

    function createCoverImage(vehicle, title) {
        var image = document.createElement("img");
        image.alt = title;
        image.loading = "lazy";

        if (isHttpUrl(vehicle.cover_image_url)) {
            // A imagem provisória só entra se a capa falhar ao carregar.
            image.addEventListener("error", function () {
                usePlaceholder(image);
            }, { once: true });
            image.src = vehicle.cover_image_url.trim();
        } else {
            usePlaceholder(image);
        }

        return image;
    }

    function createBadge(text, className) {
        var badge = document.createElement("span");
        badge.className = "badge " + className;
        badge.textContent = text;
        return badge;
    }

    function createCard(vehicle) {
        var title = vehicleTitle(vehicle);
        var isSold = vehicle.status === "sold";

        var card = document.createElement("article");
        card.className = isSold ? "card card-sold" : "card";

        var imageBox = document.createElement("div");
        imageBox.className = "card-img";
        imageBox.appendChild(createCoverImage(vehicle, title));

        if (isSold || vehicle.is_modified === true) {
            var badges = document.createElement("div");
            badges.className = "badges";
            if (isSold) {
                badges.appendChild(createBadge("Vendido", "badge-sold"));
            }
            if (vehicle.is_modified === true) {
                badges.appendChild(createBadge("Modificado", "badge-modified"));
            }
            imageBox.appendChild(badges);
        }

        var info = document.createElement("div");
        info.className = "card-info";

        var heading = document.createElement("h3");
        heading.textContent = title;

        var details = document.createElement("p");
        details.textContent = [
            vehicle.year,
            mileageFormatter.format(Number(vehicle.mileage)) + " km",
            CONDITION_LABELS[vehicle.condition]
        ].filter(function (part) {
            return part !== undefined && part !== null && part !== "";
        }).join(" · ");

        var price = document.createElement("strong");
        price.textContent = priceFormatter.format(Number(vehicle.price));

        info.appendChild(heading);
        info.appendChild(details);
        info.appendChild(price);

        card.appendChild(imageBox);
        card.appendChild(info);
        return card;
    }

    function renderVehicles(vehicles) {
        states.list.replaceChildren();

        if (vehicles.length === 0) {
            showState("empty");
            return;
        }

        vehicles.forEach(function (vehicle) {
            states.list.appendChild(createCard(vehicle));
        });
        showState("list");
    }

    function loadCatalog() {
        states.list.replaceChildren();
        showState("loading");

        var config = window.REVAULTE_CONFIG || {};
        var url = String(config.catalogApiBaseUrl || "").replace(/\/+$/, "") + "/vehicles";

        fetch(url, { headers: { Accept: "application/json" } })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Resposta HTTP " + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                if (!Array.isArray(data)) {
                    throw new Error("Resposta inesperada do catálogo");
                }
                renderVehicles(data);
            })
            .catch(function (error) {
                console.error("Falha ao carregar o catálogo:", error);
                states.list.replaceChildren();
                showState("error");
            });
    }

    retryButton.addEventListener("click", loadCatalog);
    loadCatalog();
})();
