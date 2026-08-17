export const map = L.map('map').setView([7.8891, -72.4967], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CARTO'
}).addTo(map);

map.on('click', (e) => {
    window.dispatchEvent(new CustomEvent("mapClick", {
        detail: e.latlng
    }));

});

map.on('contextmenu', (e) => {
    e.originalEvent.preventDefault();
});

const paraderoIcons = {
    inicio: L.divIcon({
        className: "",
        html: '<div class="paradero-marker paradero-marker-inicio"></div>',
        iconSize: [18, 18],
        iconAnchor: [9, 9]
    }),
    final: L.divIcon({
        className: "",
        html: '<div class="paradero-marker paradero-marker-final"></div>',
        iconSize: [18, 18],
        iconAnchor: [9, 9]
    })
};

const paraderoMarkers = {};

export function setParaderoMarker(tipo, lat, lng, nombre) {
    if (paraderoMarkers[tipo]) {
        map.removeLayer(paraderoMarkers[tipo]);
        delete paraderoMarkers[tipo];
    }
    if (lat == null || lng == null) return;

    const marker = L.marker([lat, lng], { icon: paraderoIcons[tipo] })
        .bindTooltip(nombre)
        .addTo(map);

    paraderoMarkers[tipo] = marker;
}

export function clearParaderoMarker(tipo) {
    setParaderoMarker(tipo, null, null);
}

export function getParaderoLatLng(tipo) {
    const marker = paraderoMarkers[tipo];
    return marker ? marker.getLatLng() : null;
}
