function getCookie(name) {
    return document.cookie
        .split(";")
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(`${name}=`))
        ?.split("=")[1] ?? null;
}

const csrftoken = getCookie("csrftoken");

const addBusButton = document.getElementById("add-bus");
const busForm = document.getElementById("bus-form");
const switchRastreador = document.getElementById("activar-rastreador");
const rastreadorInput = document.getElementById("rastreador-input");

const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const methodInput = busForm.querySelector('[name="method"]');

const busNumberInput = document.getElementById("id_numero_bus");
const placaInput = document.getElementById("id_placa");
const rutaInput = document.getElementById("id_ruta");
const modeloInput = document.getElementById("id_modelo");
const modeloAnioInput = document.getElementById("id_modelo_anio");
const btnSubmitForm = document.getElementById("btn-submit-form");
const addBusErrorDiv = document.getElementById("add-bus-error");

const formDrawer = new bootstrap.Offcanvas(
    document.getElementById("busDrawer")
);

function actualizarEstadoRastreador() {
    rastreadorInput.disabled = !switchRastreador.checked;
}

function limpiarFormulario() {
    busForm.reset();
    switchRastreador.checked = false;
    rastreadorInput.disabled = true;
    rastreadorInput.value = "";
}

function configurarModoAgregar() {

    limpiarFormulario();

    placaInput.disabled = false;

    formTitle.textContent = "Agregar nuevo bus";
    formSubtitle.textContent =
        "Ingresa los datos técnicos de la unidad";

    methodInput.value = "post";
    btnSubmitForm.value = "Agregar bus";
}

function configurarModoEditar(placa) {

    placaInput.disabled = true;

    formTitle.textContent = `Editar bus: ${placa}`;
    formSubtitle.textContent =
        "Actualiza los datos técnicos de la unidad";

    methodInput.value = "put";
    btnSubmitForm.value = "Actualizar bus";
}

function cargarBusEnFormulario(bus) {

    busNumberInput.value = bus.numero_bus;
    placaInput.value = bus.placa;
    modeloInput.value = bus.modelo;
    modeloAnioInput.value = bus.modelo_anio;
    rutaInput.value = bus.ruta;

    const tieneRastreador = Boolean(bus.rastreador);

    switchRastreador.checked = tieneRastreador;
    rastreadorInput.disabled = !tieneRastreador;

    const serialRastreador = bus.rastreador ?? "";

    if (serialRastreador && !rastreadorInput.querySelector(`option[value="${serialRastreador}"]`)) {
        rastreadorInput.add(new Option(serialRastreador, serialRastreador));
    }

    rastreadorInput.value = serialRastreador;
}

function ocultarErrorFormulario(){
    addBusErrorDiv.classList.add("d-none");
    addBusErrorDiv.textContent = "";
}

function mostrarErrorFormulario(data){
    let mensaje;
    if(data.message){
        mensaje = data.message;
    } else if(data.errors){
        mensaje = Object.values(data.errors)
            .flat()
            .join(" ");
    } else{
        mensaje = "Ocurrrio un error inesperado"
    }
    addBusErrorDiv.textContent = mensaje;
    addBusErrorDiv.classList.remove("d-none");
}


async function obtenerBus(placa) {

    const getBusRequest = await fetch(`/buses/${placa}`);

    if (!getBusRequest.ok) {
        throw new Error("No fue posible obtener la información del bus");
    }

    return await getBusRequest.json();
}

async function eliminarBus(placa) {

    return fetch(`${placa}`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken
        }
    });
}

addBusButton.addEventListener("click", () => {
    configurarModoAgregar();
    formDrawer.show();
});

switchRastreador.addEventListener(
    "change",
    actualizarEstadoRastreador
);

document.querySelectorAll(".btn-delete").forEach(button => {

    button.addEventListener("click", async function () {

        const { placa } = this.dataset;

        if (!confirm(`¿Desea eliminar el bus con placa ${placa}?`)) {
            return;
        }

        try {

            const deleteRequest = await eliminarBus(placa);

            if (deleteRequest.status === 204) {
                location.reload();
                return;
            }

            alert(await deleteRequest.text());

        } catch (error) {
            console.error(error);
            alert("Error de conexión");
        }
    });

});

document.querySelectorAll(".btn-update").forEach(button => {

    button.addEventListener("click", async function () {

        const { placa } = this.dataset;

        try {

            const bus = await obtenerBus(placa);

            configurarModoEditar(placa);
            cargarBusEnFormulario(bus);

            formDrawer.show();

        } catch (error) {

            console.error(error);
            alert(
                "No fue posible cargar la información del bus"
            );

        }

    });

});

const searchPlacaInput = document.getElementById("search-placa");
let searchDebounceTimer;

function filtrarBuses(termino) {
    const term = termino.toLowerCase();
    document.querySelectorAll("tbody tr").forEach(row => {
        const placa = row.dataset.placa?.toLowerCase() ?? "";
        row.style.display = placa.includes(term) ? "" : "none";
    });

    const url = new URL(window.location);
    if (termino) {
        url.searchParams.set("placa", termino);
    } else {
        url.searchParams.delete("placa");
    }
    history.replaceState(null, "", url);
}

searchPlacaInput.addEventListener("input", function () {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => filtrarBuses(this.value.trim()), 300);
});

const placaEnUrl = new URL(window.location).searchParams.get("placa");
if (placaEnUrl) {
    filtrarBuses(placaEnUrl);
}

busForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    ocultarErrorFormulario();

    const url = busForm.getAttribute("action") || window.location.pathname;

    let options;
    if (methodInput.value === "put") {
        const formData = new FormData(busForm);
        const jsonData = Object.fromEntries(formData.entries());
        jsonData.placa = placaInput.value;
        options = {
            method: "PUT",
            body: JSON.stringify(jsonData),
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            }
        };
    } else {
        options = {
            method: "POST",
            body: new FormData(busForm),
            headers: {
                "X-CSRFToken": csrftoken
            }
        };
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok) {
            mostrarErrorFormulario(data);
            return;
        }

        formDrawer.hide();
        location.reload();
    } catch (error) {
        console.error(error);
        mostrarErrorFormulario({ error: "Error de conexión" });
    }
});