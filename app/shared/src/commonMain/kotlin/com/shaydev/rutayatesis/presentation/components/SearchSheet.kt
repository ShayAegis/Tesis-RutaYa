package com.shaydev.rutayatesis.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.shaydev.rutayatesis.domain.model.Place
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource
import org.jetbrains.compose.resources.stringResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.favorite_routes_navbar
import rutaya_tesis.shared.generated.resources.ic_flag
import rutaya_tesis.shared.generated.resources.ic_marker
import rutaya_tesis.shared.generated.resources.ic_right_arrow
import rutaya_tesis.shared.generated.resources.ic_star
import rutaya_tesis.shared.generated.resources.search_route_button_title
import rutaya_tesis.shared.generated.resources.search_route_navbar
import rutaya_tesis.shared.generated.resources.search_sheet_title

@Composable
fun BottomSheetContainer(
    modifier: Modifier = Modifier,
    content: @Composable androidx.compose.foundation.layout.ColumnScope.() -> Unit,
) {
    Surface(
        modifier = modifier
            .fillMaxWidth(),
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
        tonalElevation = 6.dp,
    ) {
        Column(
            modifier = Modifier.padding(20.dp).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp),
            content = content,
        )
    }
}

@Composable
fun SearchSheetContent(
    originPlaceholder: String,
    destinationPlaceholder: String,
    onSearch: () -> Unit,
    onOriginInputChange: (String) -> Unit,
    onDestinationInputChange: (String) -> Unit,
    originSuggestions: List<Place>,
    destinationSuggestions: List<Place>,
    onOriginSuggestionSelected: (Place) -> Unit,
    onDestinationSuggestionSelected: (Place) -> Unit,
    searchEnabled: Boolean,
    walkingDistance: Float,
    onWalkingDistanceChange: (Float) -> Unit,
    isOriginLoading: Boolean = false,
    isDestinationLoading: Boolean = false,
) {
    Text(
        text = stringResource(Res.string.search_sheet_title),
        style = MaterialTheme.typography.titleLarge,
        color = MaterialTheme.colorScheme.onSurface,
        modifier = Modifier.padding(
            top = 15.dp,
            bottom = 15.dp
        ).fillMaxWidth(),
        textAlign = TextAlign.Start
    )
    PlaceInputField(
        modifier = Modifier.fillMaxWidth(),
        leadingIcon = Res.drawable.ic_marker,
        placeholder = originPlaceholder,
        suggestions = originSuggestions,
        onSuggestionSelected = onOriginSuggestionSelected,
        onTextChanged = { onOriginInputChange(it) },
        isLoading = isOriginLoading,
    )
    PlaceInputField(
        modifier = Modifier.fillMaxWidth(),
        leadingIcon = Res.drawable.ic_flag,
        placeholder = destinationPlaceholder,
        suggestions = destinationSuggestions,
        onSuggestionSelected = onDestinationSuggestionSelected,
        onTextChanged = { onDestinationInputChange(it) },
        isLoading = isDestinationLoading,
    )
    WalkingDistanceSlider(
        modifier = Modifier.padding(horizontal = 5.dp),
        onValueChange = onWalkingDistanceChange,
        valueRange = 100.0f .. 1000.0f,
        steps = 8)
    Spacer(Modifier.height(5.dp))
    PrimaryButton(
        label = stringResource(Res.string.search_route_button_title),
        onClick = onSearch,
        enabled = searchEnabled,
        modifier = Modifier.fillMaxWidth(),
        trailingIcon = Res.drawable.ic_right_arrow
    )
}

@Composable
fun BottomNavBar(
    selectedIndex: Int,
    onSelect: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 3.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .windowInsetsPadding(WindowInsets.navigationBars)
                .height(72.dp)
                .padding(horizontal = 24.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            BottomNavItem(
                label = stringResource(Res.string.search_route_navbar),
                icon = Res.drawable.ic_marker,
                selected = selectedIndex == 0,
                onClick = { onSelect(0) },
                modifier = Modifier.weight(1f),
            )
            Spacer(Modifier.width(8.dp))
            BottomNavItem(
                label = stringResource(Res.string.favorite_routes_navbar),
                icon = Res.drawable.ic_star,
                selected = selectedIndex == 1,
                onClick = { onSelect(1) },
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun BottomNavItem(
    label: String,
    icon: DrawableResource,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    selected: Boolean = false,
) {
    Column(
        modifier = modifier
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            modifier = Modifier
                .width(45.dp)
                .height(28.dp)
                .clip(RoundedCornerShape(20.dp))
                .background(
                    if (selected)
                        MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                    else Color.Transparent
                ),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                painter = painterResource(icon),
                contentDescription = "",
                modifier = Modifier.size(20.dp),
                tint = if (selected)
                    MaterialTheme.colorScheme.primary
                else Color.White
            )
        }
        Spacer(Modifier.height(4.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}
