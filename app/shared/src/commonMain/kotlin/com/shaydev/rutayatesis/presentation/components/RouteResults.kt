package com.shaydev.rutayatesis.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.snapping.rememberSnapFlingBehavior
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.shaydev.rutayatesis.domain.model.Point
import com.shaydev.rutayatesis.presentation.home.NearestBusState
import com.shaydev.rutayatesis.presentation.home.RouteResultUiModel
import org.jetbrains.compose.resources.painterResource
import org.jetbrains.compose.resources.stringResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.bus_eta_minutes
import rutaya_tesis.shared.generated.resources.bus_eta_title
import rutaya_tesis.shared.generated.resources.eta_label
import rutaya_tesis.shared.generated.resources.go_to_stop_btn_label
import rutaya_tesis.shared.generated.resources.ic_distance
import rutaya_tesis.shared.generated.resources.ic_edit
import rutaya_tesis.shared.generated.resources.ic_map
import rutaya_tesis.shared.generated.resources.ic_not_found
import rutaya_tesis.shared.generated.resources.ic_right_arrow
import rutaya_tesis.shared.generated.resources.ic_star
import rutaya_tesis.shared.generated.resources.ic_star_filled
import rutaya_tesis.shared.generated.resources.route_not_found_description
import rutaya_tesis.shared.generated.resources.route_not_found_go_back_btn
import rutaya_tesis.shared.generated.resources.route_not_found_title
import rutaya_tesis.shared.generated.resources.tracking_state_label_connected
import rutaya_tesis.shared.generated.resources.tracking_state_label_connecting
import rutaya_tesis.shared.generated.resources.tracking_state_label_no_tracking
import kotlin.math.roundToInt
import kotlin.repeat

@Composable
fun RouteResultsContent(
    routes: List<RouteResultUiModel>,
    nearestBusState: NearestBusState,
    modifier: Modifier = Modifier,
    isFavoriteButtonEnabled: Boolean = true,
    favoriteRouteIds: Set<Int> = emptySet(),
    onSelectedRouteIndexChange: (Int) -> Unit = {},
    onRouteMarkedAsFavorite: (Int) -> Unit = {},
    onGoToBoardingPoint: (Point) -> Unit = {}
) {
    val listState = rememberLazyListState()

    LaunchedEffect(listState, routes) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .collect { index ->
                onSelectedRouteIndexChange(
                    index.coerceIn(
                        0,
                        (routes.size - 1).coerceAtLeast(0)
                    )
                )
            }
    }

    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
        ) {
            repeat(routes.size) { index ->
                val isSelected = index == listState.firstVisibleItemIndex
                Box(
                    modifier = Modifier
                        .padding(horizontal = 4.dp)
                        .size(6.dp)
                        .clip(CircleShape)
                        .background(Color.White.copy(alpha = if (isSelected) 1f else 0.4f))
                )
            }
        }
        Spacer(Modifier.height(20.dp))
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            state = listState,
            flingBehavior = rememberSnapFlingBehavior(listState),
        ) {
            itemsIndexed(routes) { index, result ->
                val route = result.route
                val isSelected = index == listState.firstVisibleItemIndex
                Column(modifier = Modifier.fillParentMaxWidth()) {
                    Row(
                        modifier = Modifier.fillParentMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        BusNumberBadge(nearestBusState is NearestBusState.Found, if (nearestBusState is NearestBusState.Found) nearestBusState.bus.busNumber else null)
                        Text(
                            route.operator,
                            modifier = Modifier.padding(start = 10.dp)
                        )
                        Spacer(modifier = Modifier.weight(1.0f))
                        Box(
                            modifier = Modifier.clip(RoundedCornerShape(10.dp))
                                .background(
                                    (if (nearestBusState is NearestBusState.Found) MaterialTheme.colorScheme.primary else Color.Black).copy(
                                        alpha = 0.3f
                                    )
                                )
                                .border(
                                    width = 1.dp,
                                    shape = RoundedCornerShape(20.dp),
                                    color = if (nearestBusState is NearestBusState.Found) MaterialTheme.colorScheme.primary else Color.Black
                                )
                                .padding(all = 5.dp)
                                .padding(horizontal = 10.dp)

                        ) {
                            Text(
                                stringResource(
                                    when (nearestBusState) {
                                        NearestBusState.Idle -> Res.string.tracking_state_label_connecting
                                        is NearestBusState.Found -> Res.string.tracking_state_label_connected
                                        NearestBusState.Loading -> Res.string.tracking_state_label_connecting
                                        NearestBusState.NotFound -> Res.string.tracking_state_label_no_tracking
                                    }
                                ),
                                color = if (nearestBusState !is NearestBusState.Found) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.primary,
                                style = MaterialTheme.typography.labelMedium
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(20.dp))
                    Box(
                        modifier = Modifier.fillParentMaxWidth()
                            .border(
                                1.dp,
                                color = MaterialTheme.colorScheme.secondary,
                                shape = RoundedCornerShape(10.dp)
                            )
                            .padding(5.dp)

                    ) {
                        Row(
                            modifier = Modifier.fillParentMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            if (!route.returnWay) {
                                Text(route.originPortalName)
                                Icon(
                                    modifier = Modifier.size(16.dp),
                                    painter = painterResource(Res.drawable.ic_right_arrow),
                                    contentDescription = "Ícono hacia"
                                )
                                Text(route.destinationPortalName)
                            } else {
                                Text(route.destinationPortalName)
                                Icon(
                                    modifier = Modifier.size(16.dp),
                                    painter = painterResource(Res.drawable.ic_right_arrow),
                                    contentDescription = "Ícono hacia"
                                )
                                Text(route.originPortalName)
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(20.dp))
                    Row(
                        modifier = Modifier.fillParentMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            if (nearestBusState is NearestBusState.Found) {
                                Text(
                                    stringResource(Res.string.bus_eta_title),
                                    style = MaterialTheme.typography.titleLarge
                                )
                                Text(
                                    stringResource(
                                        Res.string.bus_eta_minutes,
                                        nearestBusState.bus.etaMinutes.roundToInt()
                                    ),
                                    color = MaterialTheme.colorScheme.primary,
                                    style = MaterialTheme.typography.titleLarge
                                )
                            }
                            Row {
                                Text(
                                    stringResource(Res.string.eta_label),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                                )
                                Text(
                                    result.arrivalTimeLabel,
                                    modifier = Modifier.padding(start = 5.dp),
                                    color = MaterialTheme.colorScheme.secondary,
                                   style = MaterialTheme.typography.labelMedium
                                )
                            }
                        }
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(5.dp))
                                .background(MaterialTheme.colorScheme.surfaceVariant)
                                .padding(10.dp)
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(
                                    painter = painterResource(Res.drawable.ic_distance),
                                    modifier = Modifier.size(32.dp),
                                    contentDescription = "Distancia del viaje",
                                    tint = MaterialTheme.colorScheme.primary
                                )
                                Text(
                                    "${route.distanceKm} km",
                                    style = MaterialTheme.typography.labelMedium
                                )

                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(20.dp))
                    Row(
                        modifier = Modifier.fillParentMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val boardingPoint = route.boardingPoint
                        PrimaryButton(
                            label = stringResource(Res.string.go_to_stop_btn_label),
                            modifier = Modifier.weight(if (isFavoriteButtonEnabled) 0.8f else 1f),
                            trailingIcon = Res.drawable.ic_map,
                            enabled = boardingPoint != null,
                            onClick = { boardingPoint?.let(onGoToBoardingPoint) })
                        if (isFavoriteButtonEnabled) {
                            val isFavorite = route.id in favoriteRouteIds
                            Box(
                                modifier = Modifier.weight(0.2f)
                                    .clickable(onClick = {
                                        onRouteMarkedAsFavorite(route.id)
                                    })
                            ) {
                                Icon(
                                    painterResource(if (isFavorite) Res.drawable.ic_star_filled else Res.drawable.ic_star),
                                    contentDescription = "Ìcono marcar ruta como favorita",
                                    modifier = Modifier.size(24.dp).align(Alignment.Center),
                                    tint = MaterialTheme.colorScheme.secondary
                                )
                            }
                        }
                    }
                }
            }
        }

    }
}

@Composable
fun NoRoutesFoundContent(
    modifier: Modifier = Modifier,
    onGoBack: () -> Unit
) {
    Column(
        modifier = modifier
            .padding(horizontal = 10.dp)
    ) {
        Icon(
            modifier = Modifier
                .size(128.dp)
                .align(Alignment.CenterHorizontally),
            painter = painterResource(Res.drawable.ic_not_found),
            contentDescription = "Ícono ruta no encontrada"
        )
        Spacer(modifier = Modifier.height(20.dp))
        Text(
            stringResource(Res.string.route_not_found_title),
            modifier = Modifier.fillMaxWidth(),
            style = MaterialTheme.typography.titleLarge,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(20.dp))
        Text(
            stringResource(Res.string.route_not_found_description),
            color = Color.White.copy(alpha = 0.6f)
        )
        PrimaryButton(
            modifier = Modifier.padding(vertical = 20.dp).fillMaxWidth(),
            label = stringResource(Res.string.route_not_found_go_back_btn),
            onClick = { onGoBack() },
            trailingIcon = Res.drawable.ic_edit
        )
    }
}
