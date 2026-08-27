package com.shaydev.rutayatesis.data.local

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import platform.Foundation.NSUserDefaults

private const val FAVORITE_ROUTE_IDS_KEY = "favorite_route_ids"

class UserDefaultsFavoriteRouteIdsCache : FavoriteRouteIdsCache {
    private val defaults = NSUserDefaults.standardUserDefaults
    private val state = MutableStateFlow(readIds())

    override val favoriteRouteIds: Flow<Set<Int>> = state

    override suspend fun add(routeId: Int) {
        persist(state.value + routeId)
    }

    override suspend fun remove(routeId: Int) {
        persist(state.value - routeId)
    }

    override suspend fun replaceAll(routeIds: Set<Int>) {
        persist(routeIds)
    }

    private fun persist(ids: Set<Int>) {
        defaults.setObject(ids.map { it.toString() }, FAVORITE_ROUTE_IDS_KEY)
        state.value = ids
    }

    private fun readIds(): Set<Int> {
        @Suppress("UNCHECKED_CAST")
        val stored = defaults.arrayForKey(FAVORITE_ROUTE_IDS_KEY) as? List<String> ?: return emptySet()
        return stored.mapNotNull { it.toIntOrNull() }.toSet()
    }
}

actual fun createFavoriteRouteIdsCache(): FavoriteRouteIdsCache = UserDefaultsFavoriteRouteIdsCache()
