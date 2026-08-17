function getCookie(name) {
    return document.cookie
        .split(";")
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(`${name}=`))
        ?.split("=")[1] ?? null;
}

const csrftoken = getCookie("csrftoken");

const conductorForm = document.getElementById("conductor-form");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const methodInput = conductorForm.querySelector('[name="method"]');
const btnSubmitForm = document.getElementById("btn-submit-form");

const cedulaInput = document.getElementById("id_cedula");
const nombresInput = document.getElementById("id_nombres");
const apellidosInput = document.getElementById("id_apellidos");
const placaBusInput = document.getElementById("id_placa_bus");

const conductorErrorDiv = document.getElementById("conductor-error");

const conductorDrawer = new bootstrap.Offcanvas(
    document.getElementById("conductorDrawer")
);

function limpiarFormulario() {
    conductorForm.reset();
}

function ocultarError() {
    conductorErrorDiv.classList.add("d-none");
    conductorErrorDiv.textContent = "";
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
    conductorErrorDiv.textContent = mensaje;
    conductorErrorDiv.classList.remove("d-none");
}

function configurarModoAgregar() {
    limpiarFormulario();
    ocultarError();
    cedulaInput.disabled = false;
    formTitle.textContent = "Agregar nuevo conductor";
    formSubtitle.textContent = "Ingresa la información del nuevo conductor";
    methodInput.value = "post";
    btnSubmitForm.textContent = "Agregar conductor";
}

function configurarModoEditar(cedula) {
    ocultarError();
    cedulaInput.disabled = true;
    formTitle.textContent = `Editar conductor: ${cedula}`;
    formSubtitle.textContent = "Actualiza la información del conductor";
    methodInput.value = "put";
    btnSubmitForm.textContent = "Guardar cambios";
}

function cargarConductorEnFormulario(data) {
    cedulaInput.value = data.cedula;
    nombresInput.value = data.nombres;
    apellidosInput.value = data.apellidos;

    const placaBus = data.placa_bus ?? "";

    if (placaBus && !placaBusInput.querySelector(`option[value="${placaBus}"]`)) {
        placaBusInput.add(new Option(placaBus, placaBus));
    }

    placaBusInput.value = placaBus;
}

async function obtenerConductor(cedula) {
    const response = await fetch(`${cedula}`);
    if (!response.ok) {
        throw new Error("No fue posible obtener la información del conductor");
    }
    return await response.json();
}

async function borrarConductor(cedula) {
    return fetch(`${cedula}`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken
        }
    });
}

document.getElementById("add-conductor").addEventListener("click", () => {
    configurarModoAgregar();
    conductorDrawer.show();
});

document.querySelectorAll(".btn-update").forEach((button) => {
    button.addEventListener("click", async function () {
        const { cedula } = this.dataset;
        try {
            const data = await obtenerConductor(cedula);
            configurarModoEditar(cedula);
            cargarConductorEnFormulario(data);
            conductorDrawer.show();
        } catch (e) {
            console.error(e);
            alert("No fue posible cargar la información del conductor");
        }
    });
});

document.querySelectorAll(".btn-delete").forEach((button) => {
    button.addEventListener("click", async function () {
        const { cedula } = this.dataset;
        if (!confirm(`¿Estás seguro de que deseas eliminar el conductor ${cedula}?`)) {
            return;
        }
        try {
            const response = await borrarConductor(cedula);
            if (response.status === 204) {
                location.reload();
                return;
            }
            alert("No se pudo eliminar el conductor");
        } catch (e) {
            console.error(e);
            alert("Error de conexión");
        }
    });
});

conductorForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarError();

    const url = window.location.pathname;
    let options;

    if (methodInput.value === "put") {
        const formData = new FormData(conductorForm);
        const jsonData = Object.fromEntries(formData.entries());
        jsonData.cedula = cedulaInput.value;
        options = {
            method: "PUT",
            body: JSON.stringify(jsonData),
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            }
        };
    } else {
        const formData = new FormData(conductorForm);
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

        conductorDrawer.hide();
        location.reload();
    } catch (e) {
        console.error(e);
        mostrarError({ message: "Error de conexión" });
    }
});
