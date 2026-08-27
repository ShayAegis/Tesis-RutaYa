package com.shaydev.rutayatesis.presentation.favorites

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shaydev.rutayatesis.data.exceptions.FavoritesAccessDenied
import com.shaydev.rutayatesis.domain.model.FavoriteRoute
import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.domain.usecase.GetAccessTokenUseCase
import com.shaydev.rutayatesis.domain.usecase.GetFavoritesUseCase
import com.shaydev.rutayatesis.domain.usecase.LogoutUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveSessionStateUseCase
import com.shaydev.rutayatesis.domain.usecase.RemoveFavoriteUseCase
import com.shaydev.rutayatesis.log.AppLogger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class FavoritesUiState(
    val sessionState: SessionState = SessionState.Unknown,
    val favorites: List<FavoriteRoute> = emptyList(),
)

class FavoritesViewModel(
    observeSessionState: ObserveSessionStateUseCase,
    private val removeFavorite: RemoveFavoriteUseCase,
    private val getFavorites: GetFavoritesUseCase,
    private val getAccessToken: GetAccessTokenUseCase,
    private val logout: LogoutUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(FavoritesUiState())
    val state: StateFlow<FavoritesUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            observeSessionState().collect { sessionState ->
                _state.update { it.copy(sessionState = sessionState) }
            }
        }
    }

    fun checkFavoritesAccess() {
        viewModelScope.launch {
            withAccessToken { token -> refreshFavorites(token) }
        }
    }

    fun onRemoveFavorite(route: FavoriteRoute) {
        viewModelScope.launch {
            withAccessToken { token ->
                runCatching { removeFavorite(token, route.id) }
                    .onSuccess {
                        _state.update { it.copy(favorites = it.favorites.filterNot { favorite -> favorite.id == route.id }) }
                    }
                    .onFailure { error -> AppLogger.error(TAG, "Error al eliminar favorito", error) }
            }
        }
    }

    private suspend fun refreshFavorites(token: String) {
        runCatching { getFavorites(token) }
            .onSuccess { favorites -> _state.update { it.copy(favorites = favorites) } }
            .onFailure { error ->
                AppLogger.error(TAG, "Error al cargar favoritos", error)
                if (error is FavoritesAccessDenied) logout()
            }
    }

    private suspend fun withAccessToken(block: suspend (String) -> Unit) {
        val token = getAccessToken()
        if (token == null) {
            logout()
            return
        }
        block(token)
    }

    companion object {
        private const val TAG = "FavoritesViewModel"
    }
}
