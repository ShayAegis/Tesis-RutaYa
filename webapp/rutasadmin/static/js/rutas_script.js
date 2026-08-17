function getCookie(name) {
    return document.cookie
        .split(";")
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(`${name}=`))
        ?.split("=")[1] ?? null;
}

const csrftoken = getCookie("csrftoken");
const routeSearchInput = document.getElementById("search-ruta")

async function eliminarRuta(id){
    return fetch(`${id}/`,{
        method:"DELETE",
        headers:{
            "X-CSRFToken": csrftoken
        }
    });
}

function filtrarRuta(codigoRuta){

    const url = new URL(window.location);

    if (codigoRuta) {
        url.searchParams.set("ruta", codigoRuta);
    } else {
        url.searchParams.delete("ruta");
    }
    url.searchParams.delete("page");
    window.location.href = url;
}

let searchDebounceTimer;

routeSearchInput.addEventListener("input", async function(){
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = setTimeout(() => filtrarRuta(this.value.trim()),500);
});

document.querySelectorAll(".btn-delete").forEach(button => {
    button.addEventListener("click",async function (){
        const { id } = this.dataset;
        if(!confirm(`¿Desea eliminar la ruta?`)){
            return;
        }
        try{

            const deleteRequest = await eliminarRuta(id);
            const deleteResponse = await deleteRequest.json();
            alert(deleteResponse.message || deleteResponse.error);

            if(deleteRequest.status === 200){
                location.reload();
            }



        } catch (error){
            console.error(error)
        }
    });
});