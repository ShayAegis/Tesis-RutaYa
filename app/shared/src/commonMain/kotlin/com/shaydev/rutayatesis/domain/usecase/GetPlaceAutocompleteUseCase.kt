package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.Place
import com.shaydev.rutayatesis.domain.repository.PlacesRepository

class GetPlaceAutocompleteUseCase(
    private val repository: PlacesRepository
) {
    suspend operator fun invoke(input: String): List<Place> {
        if(input.isBlank() || input.isEmpty()) return emptyList()
        return repository.getPlacesAutocomplete(input)
    }
}