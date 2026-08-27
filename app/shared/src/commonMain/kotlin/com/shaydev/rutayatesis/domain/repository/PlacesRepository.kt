package com.shaydev.rutayatesis.domain.repository

import com.shaydev.rutayatesis.domain.model.Place

interface PlacesRepository {
    suspend fun getPlacesAutocomplete(input:String): List<Place>
}