package com.shaydev.rutayatesis.presentation.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.input.TextFieldState
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SecureTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PasswordField(
    modifier: Modifier = Modifier,
    state: TextFieldState,
    placeholder: String?,
    leadingIcon: DrawableResource?,
    leadingIconDescription: String?,
    contentAlpha: Float = 1.0f,
    isError: Boolean = false
) {
    SecureTextField(
        state = state,
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(15.dp))
            .alpha(contentAlpha),
        placeholder = { placeholder?.let { Text(it) } },
        leadingIcon = {
            leadingIcon?.let {
                Icon(
                    modifier = Modifier.size(24.dp),
                    painter = painterResource(leadingIcon),
                    contentDescription = leadingIconDescription
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
        isError = isError
    )
}