class PuntosMuyCercanos(Exception):
    def __init__(self):
        super().__init__("Los puntos de origen y destino se encuentran muy cerca, revisalos e intentalo de nuevo")