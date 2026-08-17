import { map, setParaderoMarker, clearParaderoMarker, getParaderoLatLng } from "./crear_ruta_map.js";

function setupParaderoAutocomplete(textInputId, tipo) {
    const textInput = document.getElementById(textInputId);
    const hiddenInputId = textInputId.replace("_nombre", "");
    const hiddenInput = document.getElementById(hiddenInputId);
    const list = document.querySelector(`.paradero-suggestions[data-target="${hiddenInputId}"]`);

    if (!textInput || !hiddenInput || !list) return;

    let debounceTimer;

    function ocultarSugerencias() {
        list.classList.add("d-none");
        list.innerHTML = "";
    }

    function mostrarSugerencias(paraderos) {
        list.innerHTML = "";
        if (paraderos.length === 0) {
            ocultarSugerencias();
            return;
        }
        paraderos.forEach(paradero => {
            const item = document.createElement("li");
            item.className = "list-group-item list-group-item-action";
            item.style.cursor = "pointer";
            item.textContent = paradero.nombre;
            item.addEventListener("mousedown", (e) => {
                e.preventDefault();
                textInput.value = paradero.nombre;
                hiddenInput.value = paradero.id;
                setParaderoMarker(tipo, paradero.lat, paradero.lng, paradero.nombre);
                ocultarSugerencias();
            });
            list.appendChild(item);
        });
        list.classList.remove("d-none");
    }

    async function buscarParaderos(query) {
        try {
            const response = await fetch(`/paraderos/buscar/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            mostrarSugerencias(data.paraderos ?? []);
        } catch (error) {
            console.error(error);
        }
    }

    textInput.addEventListener("input", function () {
        hiddenInput.value = "";
        clearParaderoMarker(tipo);
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        if (!query) {
            ocultarSugerencias();
            return;
        }
        debounceTimer = setTimeout(() => buscarParaderos(query), 300);
    });

    textInput.addEventListener("blur", () => {
        setTimeout(ocultarSugerencias, 150);
    });
}

setupParaderoAutocomplete("id_punto_inicio_nombre", "inicio");
setupParaderoAutocomplete("id_punto_final_nombre", "final");

const initialParaderos = window.initialParaderos ?? {};
if (initialParaderos.inicio) {
    const { lat, lng, nombre } = initialParaderos.inicio;
    setParaderoMarker("inicio", lat, lng, nombre);
}
if (initialParaderos.final) {
    const { lat, lng, nombre } = initialParaderos.final;
    setParaderoMarker("final", lat, lng, nombre);
}

const distanciaInput = document.getElementById("id_distancia");
const recorridoInput = document.getElementById("id_recorrido");
const distanceCardDisplay = document.getElementById("distance-display");
const resetPointsButton = document.getElementById("reset-points")

const SEGMENT_COLORS = ["blue", "red"];
const PARADERO_SNAP_RADIUS_M = 40;

// segments[0] = primer tramo (azul, debe iniciar dentro del paradero de inicio)
// segments[1] = segundo tramo (rojo), se abre cuando el primer tramo toca el paradero final
let segments = [[]];
let polylineLayers = [];
let markers = [];

function isWithinParadero(latlng, tipo) {
    const paraderoLatLng = getParaderoLatLng(tipo);
    if (!paraderoLatLng) return false;
    return map.distance(latlng, paraderoLatLng) <= PARADERO_SNAP_RADIUS_M;
}

function parseInput(raw) {
    if (!raw || !raw.trim()) return [[]];
    try {
        const geojson = JSON.parse(raw);
        const type = geojson.type ?? geojson.geometry?.type;
        const coords = geojson.coordinates ?? geojson.geometry?.coordinates;
        if (!coords) return [[]];

        if (type === "MultiLineString") {
            const parsed = coords.map(line => line.map(([lng, lat]) => L.latLng(lat, lng)));
            return parsed.length > 0 ? parsed : [[]];
        }
        if (type === "LineString") {
            return [coords.map(([lng, lat]) => L.latLng(lat, lng))];
        }
        return [[]];
    } catch {
        return [[]];
    }
}

function toGeoJSON(segs) {
    return JSON.stringify({
        type: "MultiLineString",
        coordinates: segs
            .filter(seg => seg.length > 0)
            .map(seg => seg.map(p => [p.lng, p.lat]))
    });
}

function getPolylineLengthKm(segs) {
    let total = 0;
    segs.forEach(pts => {
        for (let i = 1; i < pts.length; i++) {
            total += map.distance(pts[i - 1], pts[i]);
        }
    });
    return total / 1000;
}

function renderUI() {
    const totalPoints = segments.reduce((sum, seg) => sum + seg.length, 0);
    if (totalPoints === 0) {
        distanciaInput.value = "";
        distanceCardDisplay.innerText = "0 m";
        return;
    }
    const km = getPolylineLengthKm(segments);
    distanciaInput.value = km.toFixed(3);
    distanceCardDisplay.innerText =
        km < 1
            ? (km * 1000).toFixed(0) + " m"
            : km.toFixed(2) + " km";
}

function updatePolylines() {
    polylineLayers.forEach(layer => layer && map.removeLayer(layer));
    polylineLayers = segments.map((pts, segIndex) => {
        if (pts.length < 2) return null;
        return L.polyline(pts, { color: SEGMENT_COLORS[segIndex] ?? "gray", weight: 3 }).addTo(map);
    });
}

function removePoint(segIndex, ptIndex) {
    segments[segIndex].splice(ptIndex, 1);
    if (segIndex === 1 && segments[1].length === 0) {
        segments = [segments[0]];
    }
    renderMap();
    recorridoInput.value = toGeoJSON(segments);
    renderUI();
}

function movePoint(segIndex, ptIndex, latlng) {
    segments[segIndex][ptIndex] = latlng;
    updatePolylines();
    renderUI();
}

function addMarker(latlng, segIndex, ptIndex) {
    const iconoPunto = L.divIcon({
        className: "",
        html: `<div class="punto-ruta punto-ruta-${SEGMENT_COLORS[segIndex] ?? "gray"}"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
    });

    const marker = L.marker(latlng, { draggable: true, icon: iconoPunto }).addTo(map);
    marker.segIndex = segIndex;
    marker.ptIndex = ptIndex;

    marker.on("drag", () => {
        movePoint(marker.segIndex, marker.ptIndex, marker.getLatLng());
    });

    marker.on("dragend", () => {
        movePoint(marker.segIndex, marker.ptIndex, marker.getLatLng());
        recorridoInput.value = toGeoJSON(segments);
    });

    marker.on("contextmenu", () => {
        removePoint(marker.segIndex, marker.ptIndex);
    });

    markers.push(marker);
}

function renderMap(fitView = false) {
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    segments.forEach((pts, segIndex) => {
        pts.forEach((p, ptIndex) => addMarker(p, segIndex, ptIndex));
    });

    updatePolylines();

    const bounds = polylineLayers.filter(Boolean);
    if (fitView && bounds.length > 0) {
        const group = L.featureGroup(bounds);
        map.fitBounds(group.getBounds(), { padding: [40, 40] });
    }
}

function addPoint(latlng) {
    const totalPoints = segments.reduce((sum, seg) => sum + seg.length, 0);

    if (totalPoints === 0 && !isWithinParadero(latlng, "inicio")) {
        alert("El primer punto del recorrido debe ubicarse dentro del paradero de inicio.");
        return;
    }

    const wasFirstSegment = segments.length === 1;
    const currentSegmentIndex = segments.length - 1;
    segments[currentSegmentIndex].push(latlng);

    if (wasFirstSegment && isWithinParadero(latlng, "final")) {
        segments.push([]);
    }

    renderMap();
    recorridoInput.value = toGeoJSON(segments);
    renderUI();
}

function syncFromState(fitView = false) {
    segments = parseInput(recorridoInput.value);
    renderMap(fitView);
    renderUI();
}

window.addEventListener("mapClick", (e) => {
    addPoint(e.detail);
});

syncFromState(true);

resetPointsButton.addEventListener("click", () => {
    if (!confirm("¿Estás seguro que deseas restablecer el recorrido de la ruta?")) {
        return;
    }

    recorridoInput.value = "";
    segments = [[]];
    syncFromState(false);
});
