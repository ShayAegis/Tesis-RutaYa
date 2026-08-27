package com.shaydev.rutayatesis.presentation.components

import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.input.TextFieldLineLimits
import androidx.compose.foundation.text.input.TextFieldState
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

@Composable
fun RutaYaTextField(
    state: TextFieldState,
    modifier: Modifier = Modifier,
    placeholder: String? = null,
    leadingIcon: DrawableResource? = null,
    leadingIconDescription: String? = null,
    enabled: Boolean = true,
    contentAlpha: Float = 1f,
    lineLimits: TextFieldLineLimits = TextFieldLineLimits.SingleLine,
    isError: Boolean = false
) {
    TextField(
        state = state,
        enabled = enabled,
        modifier = modifier
            .clip(RoundedCornerShape(15.dp))
            .alpha(contentAlpha),
        placeholder = placeholder?.let { text ->
            {
                Text(
                    text,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        },
        leadingIcon = leadingIcon?.let { icon ->
            {
                Icon(
                    painter = painterResource(icon),
                    contentDescription = leadingIconDescription,
                    modifier = Modifier.size(22.dp),
                )
            }
        },
        colors = TextFieldDefaults.colors(
            unfocusedIndicatorColor = Color.Transparent,
            focusedIndicatorColor = Color.Transparent,
            disabledIndicatorColor = Color.Transparent,
            errorIndicatorColor = MaterialTheme.colorScheme.error,
            focusedContainerColor = MaterialTheme.colorScheme.surfaceContainer,
            unfocusedContainerColor = MaterialTheme.colorScheme.surfaceContainer,
        ),
        lineLimits = lineLimits,
        isError = isError,
        textStyle = MaterialTheme.typography.bodyMedium
    )
}
