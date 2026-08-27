package com.shaydev.rutayatesis.presentation.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.foundation.text.input.setTextAndPlaceCursorAtEnd
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.shaydev.rutayatesis.domain.model.Place
import org.jetbrains.compose.resources.DrawableResource

@Composable
fun PlaceInputField(
    leadingIcon: DrawableResource,
    placeholder: String,
    suggestions: List<Place>,
    onSuggestionSelected: (Place) -> Unit,
    modifier: Modifier = Modifier,
    isLoading: Boolean = false,
    onTextChanged: (String) -> Unit
) {
    val textFieldState = rememberTextFieldState()
    val contentAlpha by animateFloatAsState(if (isLoading) 0.5f else 1f)

    LaunchedEffect(textFieldState){
        snapshotFlow{ textFieldState.text.toString() }
            .collect { onTextChanged(it) }
    }

    Column(modifier = modifier) {
        RutaYaTextField(
            state = textFieldState,
            placeholder = placeholder,
            leadingIcon = leadingIcon,
            contentAlpha = contentAlpha,
            modifier = modifier
        )

        if (suggestions.isNotEmpty()) {
            Surface(
                modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
                shape = RoundedCornerShape(15.dp),
                color = MaterialTheme.colorScheme.surfaceVariant,
                tonalElevation = 4.dp,
            ) {
                LazyColumn {
                    items(suggestions) { place ->
                        Text(
                            text = place.name,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    textFieldState.setTextAndPlaceCursorAtEnd(place.name)
                                    onSuggestionSelected(place)
                                }
                                .padding(horizontal = 16.dp, vertical = 12.dp),
                        )
                    }
                }
            }
        }
    }
}
