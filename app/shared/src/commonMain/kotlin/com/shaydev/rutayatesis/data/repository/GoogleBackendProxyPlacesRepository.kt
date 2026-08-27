package com.shaydev.rutayatesis.data.repository

import com.shaydev.rutayatesis.BuildKonfig
import com.shaydev.rutayatesis.data.remote.dto.PlaceDTO
import com.shaydev.rutayatesis.domain.model.Place
import com.shaydev.rutayatesis.domain.model.Point
import com.shaydev.rutayatesis.domain.repository.PlacesRepository
import com.shaydev.rutayatesis.network.NetworkUtils
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.parameter

class GoogleBackendProxyPlacesRepository(private val network: NetworkUtils): PlacesRepository {

    override suspend fun getPlacesAutocomplete(input: String): List<Place> {
        val url = "${BuildKonfig.API_BASE_URL}/lugares/autocompletar"
        val apiResponse = network.httpClient.get(url){
            parameter("lugar_ingresado",input)
        }.body<List<PlaceDTO>>()
        return apiResponse.map { it.toDomain() }
    }

    private fun PlaceDTO.toDomain() = Place(
        id = id,
        name = nombre_lugar,
        location = Point(lat = ubicacion.lat.toDouble(), lon = ubicacion.lon.toDouble()),
        matches_offset = coincidencia_hasta_indice,
    )
}