package com.shaydev.rutayatesis.presentation.search

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import cafe.adriel.voyager.core.screen.Screen
import com.shaydev.rutayatesis.domain.model.PlaceField
import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.presentation.components.BottomSheetContainer
import com.shaydev.rutayatesis.presentation.components.NoRoutesFoundContent
import com.shaydev.rutayatesis.presentation.components.RouteResultsContent
import com.shaydev.rutayatesis.presentation.components.SearchSheetContent
import com.shaydev.rutayatesis.presentation.di.LocalAppGraph
import com.shaydev.rutayatesis.presentation.directions.WalkingDirectionsLauncher
import com.shaydev.rutayatesis.presentation.home.HomeViewModel
import com.shaydev.rutayatesis.presentation.home.RouteSearchState
import com.shaydev.rutayatesis.presentation.map.PlatformMapView
import kotlinx.coroutines.flow.MutableStateFlow
import org.jetbrains.compose.resources.stringResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.destination_point_edit_text_placeholder
import rutaya_tesis.shared.generated.resources.origin_point_edit_text_placeholder
import rutaya_tesis.shared.generated.resources.searching_routes_message

class SearchScreen : Screen {

    @Composable
    override fun Content() {
        val graph = LocalAppGraph.current
        val viewModel: HomeViewModel = viewModel(factory = graph.homeViewModelFactory())
        val state by viewModel.state.collectAsStateWithLifecycle()

        val originInput = remember { MutableStateFlow("") }
        val destinationInput = remember { MutableStateFlow("") }

        LaunchedEffect(Unit) { viewModel.onSearchInputChange(PlaceField.Origin, originInput) }
        LaunchedEffect(Unit) {
            viewModel.onSearchInputChange(
                PlaceField.Destination,
                destinationInput
            )
        }

        val routeSearchState = state.routeSearchState
        val selectedRoute =
            (routeSearchState as? RouteSearchState.Success)?.routes?.getOrNull(state.selectedRouteIndex)

        Box(modifier = Modifier.fillMaxSize()) {
            PlatformMapView(
                center = HomeViewModel.DefaultCenter,
                zoom = HomeViewModel.DefaultZoom,
                modifier = Modifier.fillMaxSize(),
                originMarker = state.originPoint,
                destinationMarker = state.destinationPoint,
                busMarker = state.busTrackingData?.location,
                busBearing = state.busTrackingData?.azimuth,
                routeLine = selectedRoute?.route?.busLegPolyline.orEmpty(),
                walkingLines = selectedRoute?.route?.walkingLegPolylines.orEmpty(),
            )


            BottomSheetContainer(
                modifier = Modifier.fillMaxWidth().align(Alignment.BottomCenter),
            ) {
                when (routeSearchState) {
                    RouteSearchState.Idle -> SearchSheetContent(
                        originPlaceholder = stringResource(Res.string.origin_point_edit_text_placeholder),
                        destinationPlaceholder = stringResource(Res.string.destination_point_edit_text_placeholder),
                        onSearch = viewModel::onSearchRoute,
                        searchEnabled = state.origin != null && state.destination != null,
                        onOriginInputChange = { originInput.value = it },
                        onDestinationInputChange = { destinationInput.value = it },
                        originSuggestions = state.originSuggestions,
                        destinationSuggestions = state.destinationSuggestions,
                        onOriginSuggestionSelected = {
                            viewModel.onPlaceSelected(
                                PlaceField.Origin,
                                it
                            )
                        },
                        onDestinationSuggestionSelected = {
                            viewModel.onPlaceSelected(
                                PlaceField.Destination,
                                it
                            )
                        },
                        isOriginLoading = state.isOriginAutocompleteLoading,
                        isDestinationLoading = state.isDestinationAutocompleteLoading,
                        walkingDistance = state.walkingDistance,
                        onWalkingDistanceChange = viewModel::onWalkingDistanceChange,
                    )

                    RouteSearchState.Loading -> {
                        Column(
                            Modifier.fillMaxWidth()
                                .padding(vertical = 20.dp, horizontal = 10.dp)
                        ) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(30.dp)
                                    .align(Alignment.CenterHorizontally),
                            )
                            Spacer(modifier = Modifier.fillMaxWidth().height(15.dp))
                            Text(
                                stringResource(Res.string.searching_routes_message),
                                modifier = Modifier.fillMaxWidth(),
                                color = MaterialTheme.colorScheme.primary,
                                style = MaterialTheme.typography.titleLarge,
                                textAlign = TextAlign.Center
                            )
                        }
                    }

                    is RouteSearchState.Success -> RouteResultsContent(
                        routes = routeSearchState.routes,
                        nearestBusState = state.nearestBusState,
                        isFavoriteButtonEnabled = state.sessionState == SessionState.LoggedIn,
                        favoriteRouteIds = state.favoriteRouteIds,
                        onSelectedRouteIndexChange = viewModel::onRouteSelected,
                        onRouteMarkedAsFavorite = { viewModel.onToggleFavorite(it) },
                        onGoToBoardingPoint = { WalkingDirectionsLauncher.launch(it) },
                    )

                    RouteSearchState.Empty -> NoRoutesFoundContent(onGoBack = viewModel::onGoBackToSearch)
                }
            }
        }
    }
}
