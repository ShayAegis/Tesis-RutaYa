package com.shaydev.rutayatesis.data.repository

import com.shaydev.rutayatesis.BuildKonfig
import com.shaydev.rutayatesis.data.exceptions.FavoriteRouteAdditionFailed
import com.shaydev.rutayatesis.data.exceptions.FavoriteRouteRemovalFailed
import com.shaydev.rutayatesis.data.exceptions.FavoritesAccessDenied
import com.shaydev.rutayatesis.data.exceptions.FavoritesFetchFailed
import com.shaydev.rutayatesis.data.local.FavoriteRouteIdsCache
import com.shaydev.rutayatesis.data.location.getCurrentLocation
import com.shaydev.rutayatesis.data.remote.dto.RutaFavoritaDTO
import com.shaydev.rutayatesis.data.remote.dto.toDomain
import com.shaydev.rutayatesis.data.remote.util.decodePolyline
import com.shaydev.rutayatesis.domain.model.FavoriteRoute
import com.shaydev.rutayatesis.domain.repository.AuthRepository
import com.shaydev.rutayatesis.domain.repository.FavoritesRepository
import com.shaydev.rutayatesis.network.NetworkUtils
import io.ktor.client.call.body
import io.ktor.client.request.delete
import io.ktor.client.request.get
import io.ktor.client.request.headers
import io.ktor.client.request.parameter
import io.ktor.client.request.put
import io.ktor.client.statement.HttpResponse
import kotlinx.coroutines.flow.Flow

class ApiBackendFavoritesRepository(
    private val network: NetworkUtils,
    private val authRepository: AuthRepository,
    private val favoriteRouteIdsCache: FavoriteRouteIdsCache,
) : FavoritesRepository {

    override fun observeFavoriteRouteIds(): Flow<Set<Int>> = favoriteRouteIdsCache.favoriteRouteIds

    override suspend fun getFavorites(token: String): List<FavoriteRoute> {
        val url = "${BuildKonfig.API_BASE_URL}/usuarios/me/rutas/favoritas"
        val currentLocation = getCurrentLocation()
        val response = requestWithRefresh(token) { authToken ->
            network.httpClient.get(url) {
                headers {
                    append("Authorization", "Bearer $authToken")
                }
                currentLocation?.let {
                    parameter("posicion_actual_lat", it.lat)
                    parameter("posicion_actual_lon", it.lon)
                }
            }
        }
        when (response.status.value) {
            200 -> {}
            401, 403 -> throw FavoritesAccessDenied("El usuario ya no tiene acceso a favoritos")
            else -> throw FavoritesFetchFailed("No se pudieron cargar las rutas favoritas")
        }
        val favorites = response.body<List<RutaFavoritaDTO>>().map { it.toDomain() }
        favoriteRouteIdsCache.replaceAll(favorites.map { it.id }.toSet())
        return favorites
    }

    override suspend fun add(token: String, routeId: Int) {
        val url = "${BuildKonfig.API_BASE_URL}/usuarios/me/rutas/favoritas/$routeId"
        val response = requestWithRefresh(token) { authToken ->
            network.httpClient.put(url) {
                headers {
                    append("Authorization", "Bearer $authToken")
                }
            }
        }
        if (response.status.value == 409) {
            favoriteRouteIdsCache.add(routeId)
            throw FavoriteRouteAdditionFailed("La ruta ya está marcada como favorita")
        }
        if (response.status.value != 200) {
            throw FavoriteRouteAdditionFailed("No se pudo marcar la ruta como favorita")
        }
        favoriteRouteIdsCache.add(routeId)
    }

    override suspend fun remove(token: String, routeId: Int) {
        val url = "${BuildKonfig.API_BASE_URL}/usuarios/me/rutas/favoritas/$routeId"
        val response = requestWithRefresh(token) { authToken ->
            network.httpClient.delete(url) {
                headers {
                    append("Authorization", "Bearer $authToken")
                }
            }
        }
        if (response.status.value != 204) {
            throw FavoriteRouteRemovalFailed("No se pudo eliminar la ruta favorita")
        }
        favoriteRouteIdsCache.remove(routeId)
    }

    // Punto único donde cualquier llamada protegida de este repositorio reintenta
    // con un token nuevo si el backend responde 401 y hay refresh_token guardado.
    private suspend fun requestWithRefresh(
        token: String,
        request: suspend (token: String) -> HttpResponse,
    ): HttpResponse {
        val response = request(token)
        if (response.status.value != 401) return response
        if (!authRepository.refreshSession()) return response
        val refreshedToken = authRepository.getAccessToken() ?: return response
        return request(refreshedToken)
    }

    private fun RutaFavoritaDTO.toDomain() = FavoriteRoute(
        id = metadata.id,
        operator = metadata.empresa,
        code = metadata.codigo,
        originPortalName = metadata.paradero_inicio,
        destinationPortalName = metadata.paradero_final,
        polyline = decodePolyline(recorrido),
        nearestBus = bus_cercano?.toDomain(),
    )
}
