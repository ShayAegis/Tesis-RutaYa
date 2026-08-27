package com.shaydev.rutayatesis.data.local

import kotlinx.coroutines.flow.Flow

/**
 * Cache local de ids de rutas favoritas para que la UI pueda marcar el ícono de
 * favorito como "lleno" sin depender de una llamada de red. Se sincroniza con el
 * backend cada vez que se cargan, agregan o eliminan favoritos.
 */
interface FavoriteRouteIdsCache {
    val favoriteRouteIds: Flow<Set<Int>>
    suspend fun add(routeId: Int)
    suspend fun remove(routeId: Int)
    suspend fun replaceAll(routeIds: Set<Int>)
}

expect fun createFavoriteRouteIdsCache(): FavoriteRouteIdsCache
