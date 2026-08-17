from pyproj import Transformer
from shapely import Point
from shapely.geometry import LineString
from shapely.ops import substring, transform

from domain.entities.coordenada import Coordenada
from domain.servicios.calculador_geometria import CalculadorGeometria

_TRANSFORMADOR_WGS84_A_METROS = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)


def _a_linea(trayecto: list[Coordenada]) -> LineString:
    return LineString([(punto.lon, punto.lat) for punto in trayecto])


class ShapelyCalculadorGeometria(CalculadorGeometria):
    def proyectar_punto_en_trayecto(self, trayecto: list[Coordenada], punto: Coordenada) -> float:
        return _a_linea(trayecto).project(Point(punto.lon, punto.lat))

    def subtrayecto(self, trayecto: list[Coordenada], distancia_inicio: float, distancia_fin: float) -> list[Coordenada]:
        linea = substring(_a_linea(trayecto), distancia_inicio, distancia_fin)
        return [Coordenada(lat=lat, lon=lon) for lon, lat in linea.coords]

    def simplificar(self, trayecto: list[Coordenada], tolerancia: float) -> list[Coordenada]:
        linea = _a_linea(trayecto).simplify(tolerancia)
        return [Coordenada(lat=lat, lon=lon) for lon, lat in linea.coords]

    def longitud_metros(self, trayecto: list[Coordenada]) -> float:
        linea_proyectada = transform(_TRANSFORMADOR_WGS84_A_METROS.transform, _a_linea(trayecto))
        return linea_proyectada.length

    def distancia_puntos_metros(self, a: Coordenada, b: Coordenada) -> float:
        x_a, y_a = _TRANSFORMADOR_WGS84_A_METROS.transform(a.lon, a.lat)
        x_b, y_b = _TRANSFORMADOR_WGS84_A_METROS.transform(b.lon, b.lat)
        return Point(x_a, y_a).distance(Point(x_b, y_b))

    def punto_intersecta_trayecto(self,punto: Coordenada, trayecto: list[Coordenada], buffer: float = 0) -> bool:
        return Point(punto.lon, punto.lat).buffer(buffer).intersects(_a_linea(trayecto))