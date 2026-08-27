package com.shaydev.rutayatesis.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shaydev.rutayatesis.domain.model.BusTrackingData
import com.shaydev.rutayatesis.domain.model.NearestBus
import com.shaydev.rutayatesis.domain.model.Point
import com.shaydev.rutayatesis.domain.model.Place
import com.shaydev.rutayatesis.domain.model.PlaceField
import com.shaydev.rutayatesis.domain.model.Route
import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.domain.usecase.AddFavoriteUseCase
import com.shaydev.rutayatesis.domain.usecase.FindRouteUseCase
import com.shaydev.rutayatesis.domain.usecase.GetAccessTokenUseCase
import com.shaydev.rutayatesis.domain.usecase.GetPlaceAutocompleteUseCase
import com.shaydev.rutayatesis.domain.usecase.GetRouteArrivalTimeUseCase
import com.shaydev.rutayatesis.domain.usecase.LogoutUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveBusLocationUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveFavoriteRouteIdsUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveSessionStateUseCase
import com.shaydev.rutayatesis.domain.usecase.RemoveFavoriteUseCase
import com.shaydev.rutayatesis.domain.usecase.TrackNearestBusUseCase
import com.shaydev.rutayatesis.log.AppLogger
import com.shaydev.rutayatesis.presentation.util.toAmPmLabel
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

private const val DEFAULT_WALKING_DISTANCE = 1000f

data class RouteResultUiModel(
    val route: Route,
    val arrivalTimeLabel: String,
)

sealed interface RouteSearchState {
    data object Idle : RouteSearchState
    data object Loading : RouteSearchState
    data class Success(val routes: List<RouteResultUiModel>) : RouteSearchState
    data object Empty : RouteSearchState
}

sealed interface NearestBusState {
    data object Idle : NearestBusState
    data object Loading : NearestBusState
    data class Found(val bus: NearestBus) : NearestBusState
    data object NotFound : NearestBusState
}

data class HomeUiState(
    val sessionState: SessionState = SessionState.Unknown,
    val origin: Place? = null,
    val destination: Place? = null,
    val originPoint: Point? = null,
    val destinationPoint: Point? = null,
    val routeSearchState: RouteSearchState = RouteSearchState.Idle,
    val selectedRouteIndex: Int = 0,
    val nearestBusState: NearestBusState = NearestBusState.Idle,
    val busTrackingData: BusTrackingData? = null,
    val originSuggestions: List<Place> = emptyList(),
    val destinationSuggestions: List<Place> = emptyList(),
    val isOriginAutocompleteLoading: Boolean = false,
    val isDestinationAutocompleteLoading: Boolean = false,
    val walkingDistance: Float = DEFAULT_WALKING_DISTANCE,
    val favoriteRouteIds: Set<Int> = emptySet(),
)

class HomeViewModel(
    observeSessionState: ObserveSessionStateUseCase,
    private val findRoute: FindRouteUseCase,
    private val getPlaceAutocomplete: GetPlaceAutocompleteUseCase,
    private val getRouteArrivalTime: GetRouteArrivalTimeUseCase,
    private val trackNearestBus: TrackNearestBusUseCase,
    private val observeBusLocation: ObserveBusLocationUseCase,
    private val addFavorite: AddFavoriteUseCase,
    private val removeFavorite: RemoveFavoriteUseCase,
    observeFavoriteRouteIds: ObserveFavoriteRouteIdsUseCase,
    private val getAccessToken: GetAccessTokenUseCase,
    private val logout: LogoutUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(HomeUiState())
    val state: StateFlow<HomeUiState> = _state.asStateFlow()

    private var suppressNextOriginQuery = false
    private var suppressNextDestinationQuery = false
    private var trackNearestBusJob: Job? = null
    private var busTrackingJob: Job? = null

    init {
        viewModelScope.launch {
            observeSessionState().collect { sessionState ->
                _state.update { it.copy(sessionState = sessionState) }
            }
        }
        viewModelScope.launch {
            observeFavoriteRouteIds().collect { favoriteRouteIds ->
                _state.update { it.copy(favoriteRouteIds = favoriteRouteIds) }
            }
        }
    }

    fun onGoBackToSearch() {
        trackNearestBusJob?.cancel()
        busTrackingJob?.cancel()
        _state.update {
            it.copy(
                routeSearchState = RouteSearchState.Idle,
                selectedRouteIndex = 0,
                nearestBusState = NearestBusState.Idle,
                busTrackingData = null,
            )
        }
    }

    fun onSearchRoute() {
        val origin = _state.value.origin ?: return
        val destination = _state.value.destination ?: return
        trackNearestBusJob?.cancel()
        busTrackingJob?.cancel()
        _state.update { it.copy(routeSearchState = RouteSearchState.Loading) }
        viewModelScope.launch {
            runCatching { findRoute(origin, destination, _state.value.walkingDistance.roundToInt()) }
                .onSuccess { routes ->
                    AppLogger.debug(TAG, "Rutas encontradas: ${routes.size}")
                    val routeResults = routes.map { route ->
                        RouteResultUiModel(
                            route = route,
                            arrivalTimeLabel = getRouteArrivalTime(route).toAmPmLabel(),
                        )
                    }
                    val newState = if (routeResults.isEmpty()) RouteSearchState.Empty else RouteSearchState.Success(routeResults)
                    _state.update {
                        it.copy(
                            routeSearchState = newState,
                            selectedRouteIndex = 0,
                            nearestBusState = NearestBusState.Idle,
                            busTrackingData = null,
                        )
                    }
                }
                .onFailure { error ->
                    AppLogger.error(TAG, "Error al buscar ruta", error)
                    _state.update { it.copy(routeSearchState = RouteSearchState.Empty) }
                }
        }
    }

    fun onRouteSelected(index: Int) {
        _state.update { it.copy(selectedRouteIndex = index) }
        val routeResult = (_state.value.routeSearchState as? RouteSearchState.Success)
            ?.routes?.getOrNull(index) ?: return
        val origin = _state.value.originPoint ?: return

        trackNearestBusJob?.cancel()
        busTrackingJob?.cancel()
        _state.update { it.copy(busTrackingData = null, nearestBusState = NearestBusState.Loading) }
        trackNearestBusJob = viewModelScope.launch {
            delay(TRACK_NEAREST_BUS_DEBOUNCE_MS)
            runCatching { trackNearestBus(routeResult.route, origin) }
                .onSuccess { bus ->
                    val newState = if (bus != null) NearestBusState.Found(bus) else NearestBusState.NotFound
                    _state.update { it.copy(nearestBusState = newState) }
                    if (bus != null) startBusLocationTracking(bus)
                }
                .onFailure { error ->
                    AppLogger.error(TAG, "Error al rastrear bus cercano", error)
                    _state.update { it.copy(nearestBusState = NearestBusState.NotFound) }
                }
        }
    }

    fun onWalkingDistanceChange(value: Float) {
        _state.update { it.copy(walkingDistance = value) }
    }

    fun onToggleFavorite(routeId: Int) {
        val alreadyFavorite = routeId in _state.value.favoriteRouteIds
        viewModelScope.launch {
            val token = getAccessToken()
            if (token == null) {
                logout()
                return@launch
            }
            if (alreadyFavorite) {
                runCatching { removeFavorite(token, routeId) }
                    .onFailure { error -> AppLogger.error(TAG, "Error al quitar favorito", error) }
            } else {
                runCatching { addFavorite(token, routeId) }
                    .onFailure { error -> AppLogger.error(TAG, "Error al marcar favorito", error) }
            }
        }
    }

    private fun startBusLocationTracking(bus: NearestBus) {
        busTrackingJob = viewModelScope.launch {
            observeBusLocation(bus)
                .catch { error -> AppLogger.error(TAG, "Error al obtener ubicación del bus", error) }
                .collect { trackingData ->
                    _state.update { it.copy(busTrackingData = trackingData) }
                }
        }
    }

    @OptIn(FlowPreview::class)
    suspend fun onSearchInputChange(field: PlaceField, textFlow: Flow<String>) {
        textFlow
            .debounce(500)
            .collect { input ->
                if (consumeSuppression(field)) return@collect
                updateAutocompleteLoading(field, true)
                runCatching { getPlaceAutocomplete(input) }
                    .onSuccess { suggestions -> updateSuggestions(field, suggestions) }
                    .onFailure { error ->
                        AppLogger.error(TAG, "Error al buscar sugerencias para \"$input\"", error)
                        updateSuggestions(field, emptyList())
                    }
                updateAutocompleteLoading(field, false)
            }
    }

    fun onPlaceSelected(field: PlaceField, place: Place) {
        when (field) {
            PlaceField.Origin -> suppressNextOriginQuery = true
            PlaceField.Destination -> suppressNextDestinationQuery = true
        }
        _state.update {
            when (field) {
                PlaceField.Origin -> it.copy(
                    origin = place,
                    originPoint = place.location,
                    originSuggestions = emptyList(),
                )
                PlaceField.Destination -> it.copy(
                    destination = place,
                    destinationPoint = place.location,
                    destinationSuggestions = emptyList(),
                )
            }
        }
    }

    private fun consumeSuppression(field: PlaceField): Boolean {
        val shouldSuppress = when (field) {
            PlaceField.Origin -> suppressNextOriginQuery
            PlaceField.Destination -> suppressNextDestinationQuery
        }
        if (shouldSuppress) {
            when (field) {
                PlaceField.Origin -> suppressNextOriginQuery = false
                PlaceField.Destination -> suppressNextDestinationQuery = false
            }
        }
        return shouldSuppress
    }

    private fun updateAutocompleteLoading(field: PlaceField, isLoading: Boolean) {
        _state.update {
            when (field) {
                PlaceField.Origin -> it.copy(isOriginAutocompleteLoading = isLoading)
                PlaceField.Destination -> it.copy(isDestinationAutocompleteLoading = isLoading)
            }
        }
    }

    private fun updateSuggestions(field: PlaceField, suggestions: List<Place>) {
        _state.update {
            when (field) {
                PlaceField.Origin -> it.copy(originSuggestions = suggestions)
                PlaceField.Destination -> it.copy(destinationSuggestions = suggestions)
            }
        }
    }

    companion object {
        private const val TAG = "HomeViewModel"
        private const val TRACK_NEAREST_BUS_DEBOUNCE_MS = 2000L
        val DefaultCenter = Point(7.893174, -72.502513)
        const val DefaultZoom = 18.0
    }
}
