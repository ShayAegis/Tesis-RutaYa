from typing import Callable

from application.dto.rutas_dto import BusCercanoDTO
from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.servicios.calculador_geometria import CalculadorGeometria

#Tolerancia GPS para considerar que un bus está sobre el trayecto, en grados (~35 metros)
BUFFER_INTERSECCION_TRAYECTO = 0.00035

#Velocidad usada para estimar el ETA cuando el bus no tiene registros de velocidad en el día
VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS = 6.06


class BuscarBusCercanoPorRuta:
    def __init__(self, repositorio_buses:RepositorioBuses,
                 repositorio_rutas: RutasRepositorio,
                 calculador: CalculadorGeometria):

        self.repositorio_buses = repositorio_buses
        self.repositorio_rutas = repositorio_rutas
        self.calculador = calculador

    async def ejecutar(self, lat:float, lon:float, ruta_id:str,vuelta:bool) -> BusCercanoDTO | None:

        ruta = self.repositorio_rutas.obtener_ruta_por_codigo(ruta_id)

        if ruta is None:
            return None

        ubicacion_usuario = Coordenada(lat=lat, lon=lon)

        segmento_solicitado = ruta.recorrido[1] if vuelta else ruta.recorrido[0]
        segmento_opuesto = ruta.recorrido[0] if vuelta else ruta.recorrido[1]

        proyeccion_usuario = self.calculador.proyectar_punto_en_trayecto(segmento_solicitado, ubicacion_usuario)

        buses_segmento_solicitado = await self.repositorio_buses.obtener_bus_cercano_por_ruta(lat, lon, ruta_id, vuelta)
        buses_segmento_opuesto = await self.repositorio_buses.obtener_bus_cercano_por_ruta(lat, lon, ruta_id, not vuelta)

        bus_candidato = self._bus_con_mayor_proyeccion(
            buses_segmento_solicitado, segmento_solicitado,
            filtro=lambda proyeccion_bus: proyeccion_bus <= proyeccion_usuario,
        )

        if bus_candidato is None:
            bus_candidato = self._bus_con_mayor_proyeccion(buses_segmento_opuesto, segmento_opuesto)

        if bus_candidato is None:
            #Ningún bus cumplió la tolerancia geométrica de intersección: como último recurso
            #mostramos el bus circulando más cercano en línea recta, sin importar la distancia,
            #ya que la consulta a Mongo ya garantiza que pertenece a esta ruta.
            bus_candidato = self._bus_mas_cercano(buses_segmento_solicitado + buses_segmento_opuesto, ubicacion_usuario)

        if bus_candidato is None:
            return None

        distancia_restante_metros = self._distancia_restante_metros(
            bus_candidato, segmento_solicitado, segmento_opuesto, ubicacion_usuario, proyeccion_usuario,
        )
        eta_minutos = await self._calcular_eta_minutos(bus_candidato, distancia_restante_metros)

        return BusCercanoDTO(
            numero_bus=bus_candidato.numero_bus,
            empresa_id=bus_candidato.empresa_id,
            ruta=ruta.codigo,
            eta_minutos=eta_minutos,
        )

    def _distancia_restante_metros(
        self, bus: Bus, segmento_solicitado: list[Coordenada], segmento_opuesto: list[Coordenada],
        ubicacion_usuario: Coordenada, proyeccion_usuario: float,
    ) -> float:
        #Invariante: bus_candidato siempre proviene de _bus_con_mayor_proyeccion o
        #_bus_mas_cercano, que ya descartan buses sin ultima_ubicacion.
        assert bus.ultima_ubicacion is not None
        ubicacion_bus = bus.ultima_ubicacion

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

    def _bus_mas_cercano(self, buses: list[Bus], ubicacion_usuario: Coordenada) -> Bus | None:
        ubicaciones = [(bus, bus.ultima_ubicacion) for bus in buses if bus.ultima_ubicacion is not None]

        if not ubicaciones:
            return None

        bus_mas_cercano, _ = min(
            ubicaciones,
            key=lambda par: self.calculador.distancia_puntos_metros(ubicacion_usuario, par[1]),
        )

        return bus_mas_cercano

    def _bus_con_mayor_proyeccion(
        self, buses: list[Bus], segmento: list[Coordenada],
        filtro: Callable[[float], bool] = lambda _: True,
    ) -> Bus | None:
        mejor_bus = None
        mejor_proyeccion = -1.0

        for bus in buses:
            if bus.ultima_ubicacion is None:
                continue

            if not self.calculador.punto_intersecta_trayecto(bus.ultima_ubicacion, segmento, BUFFER_INTERSECCION_TRAYECTO):
                continue

            proyeccion_bus = self.calculador.proyectar_punto_en_trayecto(segmento, bus.ultima_ubicacion)

            if not filtro(proyeccion_bus):
                continue

            if proyeccion_bus > mejor_proyeccion:
                mejor_proyeccion = proyeccion_bus
                mejor_bus = bus

        return mejor_bus
