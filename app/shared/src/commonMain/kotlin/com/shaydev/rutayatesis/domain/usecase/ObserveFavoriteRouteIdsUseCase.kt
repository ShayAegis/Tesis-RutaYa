package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.repository.FavoritesRepository
import kotlinx.coroutines.flow.Flow

class ObserveFavoriteRouteIdsUseCase(
    private val favoritesRepository: FavoritesRepository,
) {
    operator fun invoke(): Flow<Set<Int>> = favoritesRepository.observeFavoriteRouteIds()
}
