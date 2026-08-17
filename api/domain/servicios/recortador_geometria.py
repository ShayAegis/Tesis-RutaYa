from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta

@dataclass
class RecortarGeometriaSolicitud:
    ruta: Ruta
    punto_origen: Coordenada
    punto_destino: Coordenada
    distancia_caminata: int | float

@dataclass
class GeometriaRecortada:
    recorrido: list[Coordenada]
    #Indica si el usuario debe abordar el bus en sentido de vuelta (True) o de ida (False)
    retorno: bool

class ManejadorRecorte(ABC):
    def __init__(self):
        self._siguienteManejador = SinCoincidenciaManejador()

    @abstractmethod
    def manejar(self, request: RecortarGeometriaSolicitud) -> GeometriaRecortada:
        pass

    def establecer_siguiente(self, h: ManejadorRecorte):
        self._siguienteManejador = h

class SinCoincidenciaManejador(ManejadorRecorte):
    def __init__(self):
        self._siguienteManejador = None

    def manejar(self, request):
        raise RuntimeError("Ningún handler pudo procesar la geometría")


class AmbosPuntosEnMismoSegmentoManejador(ManejadorRecorte):
    def __init__(self, calculador: CalculadorGeometria):
        super().__init__()
        self.calculador = calculador
    def manejar(self, solicitud: RecortarGeometriaSolicitud):

        segmentos = solicitud.ruta.recorrido
        distancia_caminata = solicitud.distancia_caminata
        punto_origen = solicitud.punto_origen
        punto_destino = solicitud.punto_destino


        segmentos_validos = []

        #Determinamos si ambos puntos intersectan un segmento
        for indice, segmento in enumerate(segmentos):

            if self.calculador.punto_intersecta_trayecto(punto_origen,segmento,int(distancia_caminata)) and\
               self.calculador.punto_intersecta_trayecto(punto_destino,segmento,int(distancia_caminata)):

                d_origin = self.calculador.proyectar_punto_en_trayecto(segmento,punto_origen)
                d_dest = self.calculador.proyectar_punto_en_trayecto(segmento,punto_destino)
                #Determinamos si este segmento está en el sentido correcto
                if d_dest > d_origin:
                    segmentos_validos.append((indice, segmento))

        if len(segmentos_validos) == 1:
            indice_segmento, segmento = segmentos_validos[0]
            d_origen = self.calculador.proyectar_punto_en_trayecto(segmento,punto_origen)
            d_dest = self.calculador.proyectar_punto_en_trayecto(segmento,punto_destino)
            recorrido = self.calculador.subtrayecto(segmento, d_origen, d_dest)
            #Por convención el segmento en el índice 0 es el sentido de ida
            return GeometriaRecortada(recorrido=recorrido, retorno=indice_segmento != 0)

        return self._siguienteManejador.manejar(solicitud)

class AmbosPuntosEnSegmentosDiferentes(ManejadorRecorte):
    def __init__(self, calculador: CalculadorGeometria):
        super().__init__()
        self.calculador = calculador

    def manejar(self, solicitud) -> GeometriaRecortada:

        segmentos = solicitud.ruta.recorrido
        segmento_ida, segmento_vuelta = segmentos
        distancia_caminata = solicitud.distancia_caminata

        punto_origen = solicitud.punto_origen
        punto_destino = solicitud.punto_destino

        #Determinamos en que segmento (y en que posición) intersecta el punto de origen
        origen = next(((indice, segmento) for indice, segmento in enumerate(segmentos)
                       if self.calculador.punto_intersecta_trayecto(punto_origen,segmento,distancia_caminata)),None)

        #Determinamos en que segmento (y en que posición) intersecta el punto de destino
        destino = next(((indice, segmento) for indice, segmento in enumerate(segmentos)
                        if self.calculador.punto_intersecta_trayecto(punto_destino,segmento,distancia_caminata)),None)

        if origen is not None and destino is not None:
            indice_origen, _ = origen
            indice_destino, _ = destino
            #El recorrido está ordenado ida -> vuelta, así que el segmento de origen
            #debe aparecer antes que el de destino para que el trayecto tenga sentido
            if indice_origen < indice_destino:
                distancia_origen_ida = self.calculador.proyectar_punto_en_trayecto(segmento_ida,punto_origen)
                distancia_destino_vuelta = self.calculador.proyectar_punto_en_trayecto(segmento_vuelta,punto_destino)
                subseg1 = self.calculador.subtrayecto(segmento_ida,distancia_origen_ida,self.calculador.longitud_metros(segmento_ida))
                subseg2 = self.calculador.subtrayecto(segmento_vuelta,0,distancia_destino_vuelta)
                union_coordenadas = subseg1 + subseg2
                #El usuario aborda en el segmento donde intersecta el origen
                return GeometriaRecortada(recorrido=union_coordenadas, retorno=indice_origen != 0)
        else:
            raise RuntimeError("Alguno de los puntos no intersecta a la geometria")
        siguiente_manejador=self._siguienteManejador
        siguiente_manejador.manejar(solicitud)

class RecortadorGeometria:

    def __init__(self,ruta:Ruta, calculador: CalculadorGeometria):
        self.ruta=ruta
        self.calculador = calculador
    def recortar(self,punto_origen:Coordenada,
                 punto_destino:Coordenada,
                 distancia_caminata:float) -> GeometriaRecortada:

        request=RecortarGeometriaSolicitud(
            ruta=self.ruta,
            punto_origen=punto_origen,
            punto_destino=punto_destino,
            distancia_caminata=distancia_caminata
        )

        casoA=AmbosPuntosEnMismoSegmentoManejador(self.calculador)
        casoB=AmbosPuntosEnSegmentosDiferentes(self.calculador)
        casoA.establecer_siguiente(casoB)
        geometria_recortada = casoA.manejar(request)
        return geometria_recortada