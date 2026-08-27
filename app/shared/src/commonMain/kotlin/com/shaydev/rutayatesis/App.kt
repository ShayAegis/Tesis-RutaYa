package com.shaydev.rutayatesis

import RutaYaTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import cafe.adriel.voyager.navigator.CurrentScreen
import cafe.adriel.voyager.navigator.Navigator
import com.shaydev.rutayatesis.presentation.components.BottomNavBar
import com.shaydev.rutayatesis.presentation.di.AppGraph
import com.shaydev.rutayatesis.presentation.di.LocalAppGraph
import com.shaydev.rutayatesis.presentation.favorites.FavoritesScreen
import com.shaydev.rutayatesis.presentation.search.SearchScreen

@Composable
fun App() {
    RutaYaTheme {
        val graph = remember { AppGraph() }

        CompositionLocalProvider(LocalAppGraph provides graph) {
            Navigator(SearchScreen()) { navigator ->
                Column(modifier = Modifier.fillMaxSize()) {
                    Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
                        CurrentScreen()
                    }
                    BottomNavBar(
                        selectedIndex = if (navigator.lastItem is FavoritesScreen) 1 else 0,
                        onSelect = { index ->
                            val targetIsFavorites = index == 1
                            val currentIsFavorites = navigator.lastItem is FavoritesScreen
                            if (targetIsFavorites != currentIsFavorites) {
                                navigator.replaceAll(
                                    if (targetIsFavorites) {
                                        FavoritesScreen()
                                    } else {
                                        SearchScreen()
                                    }
                                )
                            }
                        },
                    )
                }
            }
        }
    }
}
