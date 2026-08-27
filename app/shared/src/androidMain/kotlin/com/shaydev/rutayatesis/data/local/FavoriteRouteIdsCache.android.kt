package com.shaydev.rutayatesis.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.shaydev.rutayatesis.AndroidContextHolder
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.favoriteRoutesDataStore: DataStore<Preferences> by preferencesDataStore(name = "favorite_routes_cache")

private val FAVORITE_ROUTE_IDS_KEY = stringSetPreferencesKey("favorite_route_ids")

class DataStoreFavoriteRouteIdsCache(context: Context) : FavoriteRouteIdsCache {
    private val appContext = context.applicationContext

    override val favoriteRouteIds: Flow<Set<Int>> =
        appContext.favoriteRoutesDataStore.data.map { prefs ->
            prefs[FAVORITE_ROUTE_IDS_KEY]?.mapNotNull { it.toIntOrNull() }?.toSet() ?: emptySet()
        }

    override suspend fun add(routeId: Int) {
        appContext.favoriteRoutesDataStore.edit { prefs ->
            val current = prefs[FAVORITE_ROUTE_IDS_KEY] ?: emptySet()
            prefs[FAVORITE_ROUTE_IDS_KEY] = current + routeId.toString()
        }
    }

    override suspend fun remove(routeId: Int) {
        appContext.favoriteRoutesDataStore.edit { prefs ->
            val current = prefs[FAVORITE_ROUTE_IDS_KEY] ?: emptySet()
            prefs[FAVORITE_ROUTE_IDS_KEY] = current - routeId.toString()
        }
    }

    override suspend fun replaceAll(routeIds: Set<Int>) {
        appContext.favoriteRoutesDataStore.edit { prefs ->
            prefs[FAVORITE_ROUTE_IDS_KEY] = routeIds.map { it.toString() }.toSet()
        }
    }
}

actual fun createFavoriteRouteIdsCache(): FavoriteRouteIdsCache =
    DataStoreFavoriteRouteIdsCache(AndroidContextHolder.appContext)
