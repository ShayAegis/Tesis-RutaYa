package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.FavoriteRoute
import com.shaydev.rutayatesis.domain.repository.FavoritesRepository

class GetFavoritesUseCase(
    private val favoritesRepository: FavoritesRepository,
) {
    suspend operator fun invoke(token: String): List<FavoriteRoute> = favoritesRepository.getFavorites(token)
}
