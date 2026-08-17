const ubicaciones = JSON.parse(document.getElementById("ubicaciones-data").textContent);

const map = L.map('map').setView([7.8891, -72.4967], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CARTO'
}).addTo(map);

if (ubicaciones.length > 0) {
    const puntos = ubicaciones.map(u => [u.lat, u.lng]);

    L.polyline(puntos, { color: "#0d6efd", weight: 3 }).addTo(map);

    const inicioIcon = L.divIcon({
        className: "",
        html: '<div class="punto-historial punto-inicio"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    const finIcon = L.divIcon({
        className: "",
        html: '<div class="punto-historial punto-fin"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    const primera = ubicaciones[0];
    const ultima = ubicaciones[ubicaciones.length - 1];

    L.marker(puntos[0], { icon: inicioIcon })
        .bindTooltip(`Inicio: ${new Date(primera.timestamp).toLocaleTimeString()}`)
        .addTo(map);

    if (puntos.length > 1) {
        L.marker(puntos[puntos.length - 1], { icon: finIcon })
            .bindTooltip(`Último reporte: ${new Date(ultima.timestamp).toLocaleTimeString()}`)
            .addTo(map);
    }

    map.fitBounds(puntos, { padding: [40, 40] });
}
