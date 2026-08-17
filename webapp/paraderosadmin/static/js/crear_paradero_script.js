const paraderosExistentes = JSON.parse(document.getElementById("paraderos-existentes-data").textContent);

const map = L.map('map').setView([7.8891, -72.4967], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CARTO'
}).addTo(map);

const paraderoIcon = L.divIcon({
    className: "",
    html: '<div class="paradero-marker"></div>',
    iconSize: [18, 18],
    iconAnchor: [9, 9]
});

const paraderoIconExistente = L.divIcon({
    className: "",
    html: '<div class="paradero-marker paradero-marker-existente"></div>',
    iconSize: [18, 18],
    iconAnchor: [9, 9]
});

paraderosExistentes.forEach(paradero => {
    L.marker([paradero.lat, paradero.lng], { icon: paraderoIconExistente })
        .bindTooltip(paradero.nombre)
        .addTo(map);

    L.circle([paradero.lat, paradero.lng], {
        radius: paradero.radio,
        color: "#6c757d",
        weight: 1,
        fillColor: "#6c757d",
        fillOpacity: 0.1
    }).addTo(map);
});

const nombreInput = document.getElementById("id_nombre");
const codigoInput = document.getElementById("id_codigo");
const radioInput = document.getElementById("id_radio");
const latInput = document.getElementById("id_lat");
const lngInput = document.getElementById("id_lng");
const paraderoIdInput = document.getElementById("id_paradero_id");
const avisoExistente = document.getElementById("paradero-existente-aviso");
const avisoRegistrado = document.getElementById("paradero-registrado-aviso");
const avisoRegistradoCodigo = document.getElementById("paradero-registrado-codigo");
const btnCrearParadero = document.getElementById("btn-crear-paradero");

let marker = null;
let circle = null;

function getRadio() {
    const radio = parseFloat(radioInput.value);
    return Number.isFinite(radio) && radio > 0 ? radio : 0;
}

function buscarParaderoEnPunto(latlng) {
    return paraderosExistentes.find(paradero =>
        map.distance(latlng, [paradero.lat, paradero.lng]) <= paradero.radio
    );
}

function bloquearCamposParaderoExistente(bloquear) {
    nombreInput.readOnly = bloquear;
    radioInput.readOnly = bloquear;
    avisoExistente.classList.toggle("d-none", !bloquear);
}

function marcarParaderoYaRegistrado(codigo) {
    const yaRegistrado = Boolean(codigo);

    codigoInput.readOnly = yaRegistrado;
    codigoInput.value = yaRegistrado ? codigo : "";
    avisoRegistradoCodigo.textContent = codigo ?? "";
    avisoRegistrado.classList.toggle("d-none", !yaRegistrado);
    btnCrearParadero.disabled = yaRegistrado;
}

function setUbicacion(lat, lng) {
    latInput.value = lat;
    lngInput.value = lng;

    if (marker) map.removeLayer(marker);
    if (circle) map.removeLayer(circle);

    marker = L.marker([lat, lng], { icon: paraderoIcon }).addTo(map);
    circle = L.circle([lat, lng], {
        radius: getRadio(),
        color: "#0d6efd",
        weight: 1,
        fillColor: "#0d6efd",
        fillOpacity: 0.15
    }).addTo(map);
}

map.on('click', (e) => {
    const paraderoExistente = buscarParaderoEnPunto(e.latlng);

    if (paraderoExistente) {
        paraderoIdInput.value = paraderoExistente.id;
        nombreInput.value = paraderoExistente.nombre;
        radioInput.value = paraderoExistente.radio;
        bloquearCamposParaderoExistente(true);
        marcarParaderoYaRegistrado(paraderoExistente.codigo);
        setUbicacion(paraderoExistente.lat, paraderoExistente.lng);
        return;
    }

    paraderoIdInput.value = "";
    nombreInput.value = "";
    radioInput.value = "";
    bloquearCamposParaderoExistente(false);
    marcarParaderoYaRegistrado(null);
    codigoInput.value = "";
    setUbicacion(e.latlng.lat, e.latlng.lng);
});

radioInput.addEventListener("input", () => {
    if (circle) circle.setRadius(getRadio());
});

if (latInput.value && lngInput.value) {
    setUbicacion(parseFloat(latInput.value), parseFloat(lngInput.value));
    if (paraderoIdInput.value) {
        const paraderoExistente = paraderosExistentes.find(
            paradero => String(paradero.id) === paraderoIdInput.value
        );
        bloquearCamposParaderoExistente(true);
        marcarParaderoYaRegistrado(paraderoExistente?.codigo);
    }
}
