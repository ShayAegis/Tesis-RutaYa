from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.usecase.buscar_bus_cercano_por_ruta import BUFFER_INTERSECCION_TRAYECTO

#Velocidad usada para estimar el ETA cuando el bus no tiene registros de velocidad en el día
VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS = 6.06


class CalculadorEtaBus:
    def __init__(self, calculador: CalculadorGeometria, repositorio_buses: RepositorioBuses):
        self.calculador = calculador
        self.repositorio_buses = repositorio_buses

    async def calcular(
        self, bus: Bus, segmento_solicitado: list[Coordenada], segmento_opuesto: list[Coordenada],
        ubicacion_usuario: Coordenada,
    ) -> float:
        distancia_restante_metros = self._distancia_restante_metros(
            bus, segmento_solicitado, segmento_opuesto, ubicacion_usuario,
        )
        return await self._calcular_eta_minutos(bus, distancia_restante_metros)

    def _distancia_restante_metros(
        self, bus: Bus, segmento_solicitado: list[Coordenada], segmento_opuesto: list[Coordenada],
        ubicacion_usuario: Coordenada,
    ) -> float:
        #Invariante: el bus recibido siempre proviene de BuscarBusCercanoPorRuta, que ya
        #descarta buses sin ultima_ubicacion.
        assert bus.ultima_ubicacion is not None
        ubicacion_bus = bus.ultima_ubicacion

        proyeccion_usuario = self.calculador.proyectar_punto_en_trayecto(segmento_solicitado, ubicacion_usuario)

        if self.calculador.punto_intersecta_trayecto(ubicacion_bus, segmento_solicitado, BUFFER_INTERSECCION_TRAYECTO):
            proyeccion_bus = self.calculador.proyectar_punto_en_trayecto(segmento_solicitado, ubicacion_bus)

            if proyeccion_bus <= proyeccion_usuario:
                return self._distancia_subtrayecto_metros(segmento_solicitado, proyeccion_bus, proyeccion_usuario)

            #El bus ya pasó el punto del usuario en este segmento: para volver a
            #pasar por él debe completar lo que le falta del segmento actual, todo
            #el segmento opuesto y de nuevo el segmento solicitado desde el inicio
            #hasta el usuario, es decir, dar toda la vuelta a la ruta.
            fin_segmento_solicitado = self._proyeccion_fin(segmento_solicitado)
            return (
                self._distancia_subtrayecto_metros(segmento_solicitado, proyeccion_bus, fin_segmento_solicitado)
                + self.calculador.longitud_metros(segmento_opuesto)
                + self._distancia_subtrayecto_metros(segmento_solicitado, 0.0, proyeccion_usuario)
            )

        if self.calculador.punto_intersecta_trayecto(ubicacion_bus, segmento_opuesto, BUFFER_INTERSECCION_TRAYECTO):
            #El bus va en la dirección opuesta a la solicitada: debe completar lo
            #que le falta de ese segmento y luego recorrer el solicitado desde el
            #inicio hasta el usuario.
            proyeccion_bus_opuesto = self.calculador.proyectar_punto_en_trayecto(segmento_opuesto, ubicacion_bus)
            fin_segmento_opuesto = self._proyeccion_fin(segmento_opuesto)
            return (
                self._distancia_subtrayecto_metros(segmento_opuesto, proyeccion_bus_opuesto, fin_segmento_opuesto)
                + self._distancia_subtrayecto_metros(segmento_solicitado, 0.0, proyeccion_usuario)
            )

        #El bus no está sobre ninguno de los dos segmentos de la ruta: se aproxima
        #la distancia restante en línea recta.
        return self.calculador.distancia_puntos_metros(ubicacion_bus, ubicacion_usuario)

    def _proyeccion_fin(self, segmento: list[Coordenada]) -> float:
        return self.calculador.proyectar_punto_en_trayecto(segmento, segmento[-1])

    def _distancia_subtrayecto_metros(self, segmento: list[Coordenada], inicio: float, fin: float) -> float:
        #Cuando inicio y fin coinciden (o casi), el subtrayecto colapsa a un único
        #punto y shapely no puede construir una línea con él.
        if fin <= inicio:
            return 0.0
        return self.calculador.longitud_metros(self.calculador.subtrayecto(segmento, inicio, fin))

    async def _calcular_eta_minutos(self, bus: Bus, distancia_restante_metros: float) -> float:
        velocidad_promedio_kmh = await self.repositorio_buses.obtener_velocidad_promedio_diaria(
            bus.empresa_id, bus.numero_bus,
        )

        velocidad_promedio_ms = velocidad_promedio_kmh / 3.6 if velocidad_promedio_kmh else None
        if not velocidad_promedio_ms:
            velocidad_promedio_ms = VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS

        return round((distancia_restante_metros / velocidad_promedio_ms) / 60, 1)
