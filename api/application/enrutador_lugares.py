from fastapi import APIRouter, Depends

from domain.repositories.repositorio_lugares import RepositorioLugares
from domain.usecase.obtener_sugerencias_lugares import ObtenerSugerenciasLugaresCasoUso
from domain.entities.models import SugerenciaLugar
from infrastructure.dependencias import obtener_repositorio_lugares

enrutador = APIRouter(prefix="/lugares",tags=["lugares"])

@enrutador.get("/autocompletar",response_model=list[SugerenciaLugar])
async def autocompletar_lugares(lugar_ingresado:str,
                                repositorio:RepositorioLugares = Depends(obtener_repositorio_lugares)):
    caso_uso = ObtenerSugerenciasLugaresCasoUso(repositorio)
    sugerencia_lugares = await caso_uso.ejecutar(lugar_ingresado)
    return sugerencia_lugares