package com.shaydev.rutayatesis.presentation.location

import androidx.compose.runtime.Composable

@Composable
expect fun rememberLocationPermissionRequester(): () -> Unit
