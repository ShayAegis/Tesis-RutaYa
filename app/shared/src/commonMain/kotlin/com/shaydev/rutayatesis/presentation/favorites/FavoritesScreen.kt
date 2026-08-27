package com.shaydev.rutayatesis.presentation.favorites

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import cafe.adriel.voyager.core.screen.Screen
import cafe.adriel.voyager.navigator.Navigator
import com.shaydev.rutayatesis.domain.model.FavoriteRoute
import com.shaydev.rutayatesis.presentation.components.BusNumberBadge
import org.jetbrains.compose.resources.painterResource
import org.jetbrains.compose.resources.stringResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.bus_eta_minutes
import rutaya_tesis.shared.generated.resources.favorite_bus_estimated_arrival_time
import rutaya_tesis.shared.generated.resources.favorites_empty_description
import rutaya_tesis.shared.generated.resources.favorites_empty_title
import rutaya_tesis.shared.generated.resources.favorites_screen_title
import rutaya_tesis.shared.generated.resources.ic_delete
import rutaya_tesis.shared.generated.resources.ic_star
import kotlin.math.roundToInt

class FavoritesScreen : Screen {

    @Composable
    override fun Content() {
        // Nested navigator: keeps the login push/pop flow scoped to this tab,
        // so switching tabs from the bottom nav bar (replaceAll on the root
        // navigator) doesn't need to know about the auth back-stack.
        Navigator(FavoritesHomeScreen())
    }
}

@Composable
fun FavoritesScreenContent(
    favorites: List<FavoriteRoute>,
    modifier: Modifier = Modifier,
    onFavoriteSelected: (FavoriteRoute) -> Unit = {},
    onRemoveFavorite: (FavoriteRoute) -> Unit = {},
) {
    Column(
        modifier = modifier.fillMaxSize()
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(WindowInsets.statusBars.asPaddingValues())
            .padding(all = 20.dp)
    ) {
        Text(
            text = stringResource(Res.string.favorites_screen_title),
            style = MaterialTheme.typography.titleLarge,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(20.dp))
        if (favorites.isEmpty()) {
            EmptyFavoritesContent(modifier = Modifier.weight(1f))
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                items(favorites, key = { it.id }) { route ->
                    FavoriteRouteItem(
                        route = route,
                        onClick = { onFavoriteSelected(route) },
                        onRemove = { onRemoveFavorite(route) },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
    }
}

@Composable
private fun EmptyFavoritesContent(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            painter = painterResource(Res.drawable.ic_star),
            modifier = Modifier.size(96.dp),
            contentDescription = "Ícono estrella, sin favoritos",
            tint = MaterialTheme.colorScheme.primary,
        )
        Spacer(Modifier.height(20.dp))
        Text(
            text = stringResource(Res.string.favorites_empty_title),
            style = MaterialTheme.typography.titleLarge,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
            color = MaterialTheme.colorScheme.secondary
        )
        Spacer(Modifier.height(10.dp))
        Text(
            text = stringResource(Res.string.favorites_empty_description),
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun FavoriteRouteItem(
    route: FavoriteRoute,
    onClick: () -> Unit,
    onRemove: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surfaceBright)
            .clickable(true, onClick = {onClick()})
            .padding(15.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(modifier = Modifier.weight(0.8f)) {
                Text(
                    route.operator,
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "${route.originPortalName} - ${route.destinationPortalName}",
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            Box(
                modifier = Modifier.clickable(
                    true,
                    onClick = { onRemove(route.id) }
                ).weight(0.2f),
            ) {
                Icon(
                    painterResource(Res.drawable.ic_delete),
                    modifier = Modifier.align(Alignment.Center),
                    contentDescription = "Ìcono borrar ruta favorita",
                    tint = MaterialTheme.colorScheme.onSurface
                )
            }
        }
        Spacer(Modifier.height(10.dp))
        Row(modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween) {
            BusNumberBadge(route.nearestBus != null, route.nearestBus?.busNumber)
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    route.nearestBus?.let {
                        stringResource(Res.string.bus_eta_minutes, it.etaMinutes.roundToInt())
                    } ?: "--",
                    color = MaterialTheme.colorScheme.primary,
                    style = MaterialTheme.typography.labelMedium
                )
                Text(
                    stringResource(Res.string.favorite_bus_estimated_arrival_time),
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }
    }
}
