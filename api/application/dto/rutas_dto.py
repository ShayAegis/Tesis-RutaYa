from typing import List

import polyline
from pydantic import BaseModel

from domain.entities.coordenada import Coordenada
from domain.entities.itinerario import Itinerario
from domain.entities.ruta import Ruta
from domain.entities.ruta_encontrada import RutaEncontrada
from domain.entities.pierna import BusPierna, Pierna
from domain.servicios.calculador_geometria import CalculadorGeometria


class BusCercanoDTO(BaseModel):
    numero_bus: int
    empresa_id: int
    ruta: str
    eta_minutos: float

class RutaMetadataDTO(BaseModel):
    id: int
    empresa: str
    codigo: str
    paradero_inicio: str
    paradero_final: str

    @classmethod
    def desde_dominio(cls, ruta: Ruta) -> "RutaMetadataDTO":
        return cls(
            id=ruta.id,
            empresa=ruta.empresa_nombre,
            codigo=ruta.codigo,
            paradero_inicio=ruta.paradero_inicio_nombre,
            paradero_final=ruta.paradero_final_nombre,
        )

class PiernaDTO(BaseModel):
    perfil: str
    geometria: str
    punto_inicio: Coordenada
    punto_final: Coordenada
    distancia: float
    duracion: float
    peso: float

    @classmethod
    def desde_dominio(cls, pierna: Pierna) -> PiernaDTO:
        return cls(
            perfil=pierna.perfil,
            geometria=polyline.encode([(c.lat, c.lon) for c in pierna.coordenadas]),
            punto_inicio=pierna.punto_inicio,
            punto_final=pierna.punto_final,
            distancia=pierna.distancia,
            duracion=pierna.duracion,
            peso=pierna.peso,
        )

class ViajeDTO(BaseModel):
    itinerario: List[PiernaDTO]
    distancia: float
    eta: float
    peso: float
    numero_transbordos: int
    punto_abordaje: Coordenada | None = None

    @classmethod
    def desde_dominio(cls, itinerario: Itinerario, origen: Coordenada, calculador: CalculadorGeometria) -> "ViajeDTO":
        punto_abordaje = None
        primer_bus = next((pierna for pierna in itinerario.piernas if isinstance(pierna, BusPierna)), None)
        if primer_bus is not None:
            punto_abordaje = calculador.punto_abordaje(primer_bus.coordenadas, origen)

        return cls(
            itinerario=[PiernaDTO.desde_dominio(pierna) for pierna in itinerario.piernas],
            distancia=itinerario.distancia,
            eta=itinerario.eta,
            peso=itinerario.peso,
            numero_transbordos=itinerario.numero_transbordos,
            punto_abordaje=punto_abordaje,
        )

class RutasEncontradasDTO(BaseModel):
    metadata: RutaMetadataDTO
    viaje: ViajeDTO
    retorno: bool

    @classmethod
    def desde_dominio(cls, ruta_encontrada: RutaEncontrada, itinerario: Itinerario, origen: Coordenada, calculador: CalculadorGeometria) -> "RutasEncontradasDTO":
        return cls(
            metadata=RutaMetadataDTO.desde_dominio(ruta_encontrada.ruta),
            viaje=ViajeDTO.desde_dominio(itinerario, origen, calculador),
            retorno=ruta_encontrada.retorno,
        )

    @classmethod
    def lista_desde_dominio(cls, rutas_itinerarios: list[tuple[RutaEncontrada,Itinerario]], origen: Coordenada, calculador: CalculadorGeometria) -> List[
        "RutasEncontradasDTO"]:
        rutas_dto = [cls.desde_dominio(ruta_itinerario[0],ruta_itinerario[1],origen,calculador) for ruta_itinerario in rutas_itinerarios]
        return sorted(rutas_dto, key=lambda ruta_dto: ruta_dto.viaje.peso)

class RutaFavoritaDTO(BaseModel):
    metadata: RutaMetadataDTO
    recorrido: str
    bus_cercano: BusCercanoDTO | None = None

    @classmethod
    def desde_dominio(cls, ruta: Ruta, bus_cercano: BusCercanoDTO | None = None) -> "RutaFavoritaDTO":
        return cls(
            metadata=RutaMetadataDTO.desde_dominio(ruta),
            recorrido=polyline.encode([
                (c.lat, c.lon)
                for linea in ruta.recorrido
                for c in linea
            ]),
            bus_cercano=bus_cercano,
        )