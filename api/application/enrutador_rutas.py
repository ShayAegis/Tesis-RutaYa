from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from application.adapters.bus_cercano_adapter import BusCercanoAdapter
from application.dto.rutas_dto import BusCercanoDTO, RutaDTO
from application.models.error_response import ErrorResponse
from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.itinerario import Itinerario
from domain.entities.ruta_encontrada import RutaEncontrada
from domain.entities.models import Coordenada
from domain.exceptions.puntos_muy_cercanos_excepcion import PuntosMuyCercanos
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.servicios.calculador_eta_bus import CalculadorEtaBus
from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.servicios.construir_itinerario import ConstruirItinerarioServicio
from domain.usecase.buscar_bus_cercano_por_ruta import BuscarBusCercanoPorRuta
from domain.usecase.buscar_ruta_cercana import BuscarRutaCercana
from infrastructure.dependencias import obtener_repositorio_buses, obtener_repositorio_rutas, obtener_calculador_geometria
enrutador = APIRouter(prefix="/rutas", tags=["rutas"])

@enrutador.get("/{ruta_id}/bus-cercano", status_code=status.HTTP_200_OK,tags=["rutas"],response_model=BusCercanoDTO)
async def bus_cercano(ruta_id:str, lat:float, lon:float, vuelta:bool,
                      repositorio_buses: RepositorioBuses = Depends(obtener_repositorio_buses),
                      repositorio_rutas: RutasRepositorio = Depends(obtener_repositorio_rutas),
                      calculador: CalculadorGeometria = Depends(obtener_calculador_geometria)):

    caso_uso = BuscarBusCercanoPorRuta(repositorio_buses,repositorio_rutas,calculador)
    adapter = BusCercanoAdapter(caso_uso, CalculadorEtaBus(calculador, repositorio_buses))
    bus_cercano_encontrado = await adapter.ejecutar(lat,lon,ruta_id,vuelta)

    if bus_cercano_encontrado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontró un bus cercano en la ruta indicada")
    return bus_cercano_encontrado

@enrutador.get("/buscar-cercana",status_code=status.HTTP_200_OK,tags=["rutas"],
               response_model=List[RutaDTO],
               responses={404:{
                   "model":ErrorResponse,
                   "description":"Ruta no encontrada"
               }})
async def buscar_ruta_cercana(origin_lat:float,origin_lon:float,
                              dest_lat:float,dest_lon:float,
                              distancia_caminata:int,
                              repositorio:RutasRepositorio = Depends(obtener_repositorio_rutas),
                              calculador: CalculadorGeometria = Depends(obtener_calculador_geometria)):
    caso_uso = BuscarRutaCercana(repositorio,calculador)
    busqueda = BusquedaRuta(
                origen=Coordenada(lat=origin_lat,lon=origin_lon),
                destino=Coordenada(lat=dest_lat,lon=dest_lon),
                distancia_caminata=distancia_caminata
            )
    try:
        rutas_encontradas = await caso_uso.ejecutar(busqueda)
    except PuntosMuyCercanos as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(ex))
    if len(rutas_encontradas) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontraron rutas cercanas")

    construir_itinerario_servicio = ConstruirItinerarioServicio(repositorio,calculador)

    rutas_itinerarios: list[tuple[RutaEncontrada,Itinerario]] = []

    for ruta in rutas_encontradas:
        itinerario, retorno = await construir_itinerario_servicio.construir(ruta,busqueda)
        rutas_itinerarios.append((RutaEncontrada(ruta=ruta,retorno=retorno),itinerario))

    return RutaDTO.lista_desde_dominio(rutas_itinerarios, busqueda.origen, calculador)