from collections.abc import AsyncIterable

from fastapi import APIRouter, Depends, Request
from fastapi.sse import EventSourceResponse

from application.dto.buses_dto import ActualizacionUbicacionDTO
from domain.repositories.repositorio_transmision_ubicacion_bus import RepositorioTransmisionUbicacionBus
from domain.usecase.transmitir_ubicacion_bus import TransmitirUbicacionBus
from infrastructure.dependencias import obtener_repositorio_transmision_ubicacion_bus

enrutador = APIRouter(prefix="/buses", tags=["buses"])


@enrutador.get("/{numero_bus}/ubicacion/stream",response_class=EventSourceResponse)
async def ubicacion_stream(request: Request, empresaId: int, rutaId: str, numero_bus: int,
                           repositorio: RepositorioTransmisionUbicacionBus = Depends(obtener_repositorio_transmision_ubicacion_bus)) -> AsyncIterable[ActualizacionUbicacionDTO]:
    caso_uso = TransmitirUbicacionBus(repositorio)

    async for contenido in caso_uso.ejecutar(empresaId, rutaId, numero_bus):
        if await request.is_disconnected():
            break
        yield contenido
