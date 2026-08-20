from application.dto.rutas_dto import BusCercanoDTO
from domain.entities.coordenada import Coordenada
from domain.servicios.calculador_eta_bus import CalculadorEtaBus
from domain.usecase.buscar_bus_cercano_por_ruta import BuscarBusCercanoPorRuta


class BusCercanoAdapter:
    def __init__(self, caso_uso: BuscarBusCercanoPorRuta, calculador_eta: CalculadorEtaBus):
        self.caso_uso = caso_uso
        self.calculador_eta = calculador_eta

    async def ejecutar(self, lat: float, lon: float, ruta_id: str, vuelta: bool) -> BusCercanoDTO | None:
        resultado = await self.caso_uso.ejecutar(lat, lon, ruta_id, vuelta)

        if resultado is None:
            return None

        bus, ruta = resultado
        segmento_solicitado = ruta.recorrido[1] if vuelta else ruta.recorrido[0]
        segmento_opuesto = ruta.recorrido[0] if vuelta else ruta.recorrido[1]

        ubicacion_usuario = Coordenada(lat=lat, lon=lon)
        eta_minutos = await self.calculador_eta.calcular(bus, segmento_solicitado, segmento_opuesto, ubicacion_usuario)

        return BusCercanoDTO(
            numero_bus=bus.numero_bus,
            empresa_id=bus.empresa_id,
            ruta=ruta.codigo,
            eta_minutos=eta_minutos,
        )
