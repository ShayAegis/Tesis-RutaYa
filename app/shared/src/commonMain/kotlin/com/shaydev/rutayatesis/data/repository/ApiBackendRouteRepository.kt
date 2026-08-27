package com.shaydev.rutayatesis.data.repository

import com.shaydev.rutayatesis.BuildKonfig
import com.shaydev.rutayatesis.data.remote.dto.BusCercanoDTO
import com.shaydev.rutayatesis.data.remote.dto.RouteDTO
import com.shaydev.rutayatesis.data.remote.dto.toDomain
import com.shaydev.rutayatesis.data.remote.util.decodePolyline
import com.shaydev.rutayatesis.domain.model.NearestBus
import com.shaydev.rutayatesis.domain.model.Place
import com.shaydev.rutayatesis.domain.model.Point
import com.shaydev.rutayatesis.domain.model.Route
import com.shaydev.rutayatesis.domain.repository.RouteRepository
import com.shaydev.rutayatesis.network.NetworkUtils
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.parameter
import io.ktor.http.HttpStatusCode
import kotlin.math.round

private const val BUS_LEG_PROFILE = "bus"
private const val WALKING_LEG_PROFILE = "walking"

class ApiBackendRouteRepository(private val network: NetworkUtils) : RouteRepository {
    override suspend fun findRoutes(origin: Place, destination: Place, walkingDistance: Int): List<Route> {
        val url = "${BuildKonfig.API_BASE_URL}/rutas/buscar-cercana"
        val apiResponse = network.httpClient.get(url) {
            parameter("origin_lat", origin.location.lat)
            parameter("origin_lon", origin.location.lon)
            parameter("dest_lat", destination.location.lat)
            parameter("dest_lon", destination.location.lon)
            parameter("distancia_caminata", walkingDistance)
        }.body<List<RouteDTO>>()
        return apiResponse.map { it.toDomain() }
    }

    override suspend fun findNearestBus(routeCode: String, origin: Point, returnWay: Boolean): NearestBus? {
        val url = "${BuildKonfig.API_BASE_URL}/rutas/$routeCode/bus-cercano"
        val response = network.httpClient.get(url) {
            parameter("lat", origin.lat)
            parameter("lon", origin.lon)
            parameter("vuelta", returnWay)
        }
        if (response.status == HttpStatusCode.NotFound) return null
        return response.body<BusCercanoDTO>().toDomain()
    }

    private fun RouteDTO.toDomain() = Route(
        id = metadata.id,
        operator = metadata.empresa,
        code = metadata.codigo,
        distanceKm = (round(viaje.distancia / 100.0) / 10).toFloat(),
        etaSeconds = viaje.eta,
        originPortalName = metadata.paradero_inicio,
        destinationPortalName = metadata.paradero_final,
        returnWay = retorno,
        busLegPolyline = viaje.itinerario
            .filter { it.perfil == BUS_LEG_PROFILE }
            .flatMap { decodePolyline(it.geometria) },
        walkingLegPolylines = viaje.itinerario
            .filter { it.perfil == WALKING_LEG_PROFILE }
            .map { decodePolyline(it.geometria) },
        boardingPoint = viaje.punto_abordaje
            ?.let { Point(it.lat, it.lon) },
    )
}
