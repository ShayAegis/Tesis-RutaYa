function getCookie(name) {
    return document.cookie
        .split(";")
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(`${name}=`))
        ?.split("=")[1] ?? null;
}

const csrftoken = getCookie("csrftoken");

const rastreadorForm = document.getElementById("rastreador-form");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const methodInput = rastreadorForm.querySelector('[name="method"]');
const btnSubmitForm = document.getElementById("btn-submit-form");

const serialInput = document.getElementById("id_serial");
const modeloInput = document.getElementById("id_modelo");
const imeiInput = document.getElementById("id_imei");
const iccidInput = document.getElementById("id_iccid");
const numeroInput = document.getElementById("id_numero");
const operadorInput = document.getElementById("id_operador");

const rastreadorErrorDiv = document.getElementById("rastreador-error");

const rastreadorDrawer = new bootstrap.Offcanvas(
    document.getElementById("rastreadorDrawer")
);

function limpiarFormulario() {
    rastreadorForm.reset();
}

function ocultarError() {
    rastreadorErrorDiv.classList.add("d-none");
    rastreadorErrorDiv.textContent = "";
}

function mostrarError(data) {
    let mensaje;
    if (data.message) {
        mensaje = data.message;
    } else if (data.errors) {
        mensaje = Object.values(data.errors).flat().join(" ");
    } else {
        mensaje = "Ocurrió un error inesperado";
    }
    rastreadorErrorDiv.textContent = mensaje;
    rastreadorErrorDiv.classList.remove("d-none");
}

function configurarModoAgregar() {
    limpiarFormulario();
    ocultarError();
    serialInput.disabled = false;
    formTitle.textContent = "Agregar nuevo rastreador";
    formSubtitle.textContent = "Ingresa la información del nuevo rastreador";
    methodInput.value = "post";
    btnSubmitForm.textContent = "Agregar rastreador";
}

function configurarModoEditar(serial) {
    ocultarError();
    serialInput.disabled = true;
    formTitle.textContent = `Editar rastreador: ${serial}`;
    formSubtitle.textContent = "Actualiza la información del rastreador";
    methodInput.value = "put";
    btnSubmitForm.textContent = "Guardar cambios";
}

function cargarRastreadorEnFormulario(data) {
    serialInput.value = data.serial;
    modeloInput.value = data.modelo;
    imeiInput.value = data.imei;
    iccidInput.value = data.iccid;
    numeroInput.value = data.numero_sim;
    operadorInput.value = data.operador_red_id;
}

async function obtenerRastreador(serial) {
    const response = await fetch(`${serial}`);
    if (!response.ok) {
        throw new Error("No fue posible obtener la información del rastreador");
    }
    return await response.json();
}

async function borrarRastreador(serial) {
    return fetch(`${serial}`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken
        }
    });
}

document.getElementById("add-rastreador").addEventListener("click", () => {
    configurarModoAgregar();
    rastreadorDrawer.show();
});

document.querySelectorAll(".btn-update").forEach((button) => {
    button.addEventListener("click", async function () {
        const { serial } = this.dataset;
        try {
            const data = await obtenerRastreador(serial);
            configurarModoEditar(serial);
            cargarRastreadorEnFormulario(data);
            rastreadorDrawer.show();
        } catch (e) {
            console.error(e);
            alert("No fue posible cargar la información del rastreador");
        }
    });
});

document.querySelectorAll(".btn-delete").forEach((button) => {
    button.addEventListener("click", async function () {
        const { serial } = this.dataset;
        if (!confirm(`¿Estás seguro de que deseas eliminar el rastreador ${serial}?`)) {
            return;
        }
        try {
            const response = await borrarRastreador(serial);
            if (response.status === 204) {
                location.reload();
                return;
            }
            alert("No se pudo eliminar el rastreador");
        } catch (e) {
            console.error(e);
            alert("Error de conexión");
        }
    });
});

rastreadorForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarError();

    const url = window.location.pathname;
    let options;

    if (methodInput.value === "put") {
        const formData = new FormData(rastreadorForm);
        const jsonData = Object.fromEntries(formData.entries());
        jsonData.serial = serialInput.value;
        options = {
            method: "PUT",
            body: JSON.stringify(jsonData),
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            }
        };
    } else {
        const formData = new FormData(rastreadorForm);
        formData.delete("method");
        options = {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrftoken
            }
        };
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok) {
            mostrarError(data);
            return;
        }

        rastreadorDrawer.hide();
        location.reload();
    } catch (e) {
        console.error(e);
        mostrarError({ message: "Error de conexión" });
    }
});