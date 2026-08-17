const rutasData = JSON.parse(document.getElementById("rutas-data").textContent);

const map = L.map('map').setView([7.8891, -72.4967], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CARTO'
}).addTo(map);

const bounds = [];

rutasData.forEach(ruta => {
    const lines = ruta.recorrido.coordinates.map(
        line => line.map(([lng, lat]) => [lat, lng])
    );

    if (lines.some(line => line.length > 1)) {
        L.polyline(lines, { color: "blue", weight: 3 })
            .bindTooltip(ruta.codigo)
            .addTo(map);
        lines.forEach(line => bounds.push(...line));
    }
});

if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [40, 40] });
}
