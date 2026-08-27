package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.repository.FavoritesRepository

class RemoveFavoriteUseCase(
    private val favoritesRepository: FavoritesRepository,
) {
    suspend operator fun invoke(token: String, routeId: Int) = favoritesRepository.remove(token, routeId)
}
