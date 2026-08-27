package com.shaydev.rutayatesis.presentation.di

import androidx.compose.runtime.staticCompositionLocalOf

val LocalAppGraph = staticCompositionLocalOf<AppGraph> {
    error("LocalAppGraph not provided. Wrap the composition with CompositionLocalProvider(LocalAppGraph provides ...).")
}
