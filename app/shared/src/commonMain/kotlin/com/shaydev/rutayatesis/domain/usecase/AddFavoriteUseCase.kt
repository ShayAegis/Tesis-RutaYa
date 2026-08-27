package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.repository.FavoritesRepository

class AddFavoriteUseCase(
    private val favoritesRepository: FavoritesRepository,
) {
    suspend operator fun invoke(token: String, routeId: Int) = favoritesRepository.add(token, routeId)
}
