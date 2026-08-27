package com.shaydev.rutayatesis.domain.repository

import com.shaydev.rutayatesis.domain.model.FavoriteRoute
import kotlinx.coroutines.flow.Flow

interface FavoritesRepository {
    suspend fun getFavorites(token: String): List<FavoriteRoute>
    suspend fun add(token: String, routeId: Int)
    suspend fun remove(token: String, routeId: Int)
    fun observeFavoriteRouteIds(): Flow<Set<Int>>
}
