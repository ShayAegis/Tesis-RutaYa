const busesData = JSON.parse(document.getElementById("buses-data").textContent);

const POLL_INTERVALO_MS = 10000;

const map = L.map('map').setView([7.8891, -72.4967], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
}).addTo(map);

const marcadoresPorNumeroBus = new Map();

function popupHtml(bus) {
    const hora = new Date(bus.timestamp).toLocaleTimeString();
    return `<strong>Bus ${bus.numeroBus}</strong><br>Última ubicación: ${hora}`;
}

function iconoBus(bus) {
    return L.divIcon({
        className: "",
        html: `<div class="bus-marker">${bus.numeroBus}</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
    });
}

function actualizarMapa(buses, ajustarVista) {
    const bounds = [];

    buses.forEach(bus => {
        const coords = [bus.lat, bus.lon];
        bounds.push(coords);

        const marcador = marcadoresPorNumeroBus.get(bus.numeroBus);
        if (marcador) {
            marcador.setLatLng(coords).setPopupContent(popupHtml(bus));
        } else {
            const nuevoMarcador = L.marker(coords, { icon: iconoBus(bus) }).bindPopup(popupHtml(bus)).addTo(map);
            marcadoresPorNumeroBus.set(bus.numeroBus, nuevoMarcador);
        }
    });

    if (ajustarVista && bounds.length > 0) {
        map.fitBounds(bounds, { padding: [40, 40] });
    }
}

async function refrescarUbicaciones() {
    try {
        const respuesta = await fetch("ubicaciones/");
        if (!respuesta.ok) return;

        const datos = await respuesta.json();
        actualizarMapa(datos.buses_mapa, false);
    } catch (error) {
        console.error("No se pudo refrescar las ubicaciones de los buses", error);
    }
}

actualizarMapa(busesData, true);
setInterval(refrescarUbicaciones, POLL_INTERVALO_MS);
