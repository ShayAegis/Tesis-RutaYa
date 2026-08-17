import asyncio
from typing import cast
from domain.entities.models import SugerenciaLugar, Coordenada
from domain.repositories.repositorio_lugares import RepositorioLugares

class ObtenerSugerenciasLugaresCasoUso:
    def __init__(self, repositorio:RepositorioLugares):
        self.repositorio = repositorio

    async def ejecutar(self,lugar_ingresado:str) -> list[SugerenciaLugar]:
        cucuta_centro = Coordenada(lat=7.8932095858102835, lon=-72.50252943731259)
        radio_busqueda = 15000

        autocompletado_lugares = await self.repositorio.autocompletar_lugar(lugar_ingresado,cucuta_centro,radio_busqueda)
        if not autocompletado_lugares:
            return []

        sugerencia_lugares = []
        lugares = autocompletado_lugares.suggestions

        for lugar in lugares:

            matches = lugar.placePrediction.text.matches
            lugar_ubicacion_cache = self.repositorio.obtener_lugar_desde_cache("lugares_sugeridos",lugar.placePrediction.placeId)

            if lugar_ubicacion_cache:
                sugerencia_lugar = SugerenciaLugar(
                    id=lugar.placePrediction.placeId,
                    nombre_lugar=lugar.placePrediction.text.text,
                    ubicacion=lugar_ubicacion_cache,
                    coincidencia_hasta_indice=matches[0].endOffset if matches else None
                )
                sugerencia_lugares.append(sugerencia_lugar)
            else:
                lugar_ubicacion_api = await self.repositorio.obtener_ubicacion_de_lugar_por_id(
                    lugar.placePrediction.placeId
                )

                if not lugar_ubicacion_api:
                    continue

                sugerencia_lugar = SugerenciaLugar(
                    id=lugar.placePrediction.placeId,
                    nombre_lugar=lugar.placePrediction.text.text,
                    ubicacion=lugar_ubicacion_api,
                    coincidencia_hasta_indice=matches[0].endOffset if matches else None,
                )
                self.repositorio.guardar_lugar_en_cache("lugares_sugeridos", sugerencia_lugar)
                sugerencia_lugares.append(sugerencia_lugar)
        return sugerencia_lugares
