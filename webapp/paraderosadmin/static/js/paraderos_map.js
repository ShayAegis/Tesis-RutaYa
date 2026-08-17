const paraderosData = JSON.parse(document.getElementById("paraderos-data").textContent);

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

const bounds = [];

paraderosData.forEach(paradero => {
    L.marker([paradero.lat, paradero.lng], { icon: paraderoIcon })
        .bindTooltip(paradero.nombre)
        .addTo(map);

    L.circle([paradero.lat, paradero.lng], {
        radius: paradero.radio,
        color: "#0d6efd",
        weight: 1,
        fillColor: "#0d6efd",
        fillOpacity: 0.15
    }).addTo(map);

    bounds.push([paradero.lat, paradero.lng]);
});

if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [40, 40] });
}
