package com.shaydev.rutayatesis.presentation.favorites

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import cafe.adriel.voyager.core.screen.Screen
import cafe.adriel.voyager.navigator.LocalNavigator
import cafe.adriel.voyager.navigator.currentOrThrow
import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.presentation.di.LocalAppGraph
import com.shaydev.rutayatesis.presentation.location.rememberLocationPermissionRequester
import com.shaydev.rutayatesis.presentation.login.LoginScreen

class FavoritesHomeScreen : Screen {

    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow
        val graph = LocalAppGraph.current
        val viewModel: FavoritesViewModel = viewModel(factory = graph.favoritesViewModelFactory())
        val state by viewModel.state.collectAsStateWithLifecycle()
        val requestLocationPermission = rememberLocationPermissionRequester()

        LaunchedEffect(Unit) {
            viewModel.checkFavoritesAccess()
        }

        LaunchedEffect(state.sessionState) {
            when (state.sessionState) {
                SessionState.LoggedOut -> if (navigator.lastItem !is LoginScreen) {
                    navigator.push(LoginScreen())
                }

                SessionState.LoggedIn -> {
                    if (navigator.lastItem is LoginScreen) {
                        navigator.pop()
                    }
                    requestLocationPermission()
                }

                SessionState.Unknown -> Unit
            }
        }

        if (state.sessionState == SessionState.LoggedIn) {
            FavoritesScreenContent(
                favorites = state.favorites,
                modifier = Modifier.fillMaxSize(),
                onRemoveFavorite = viewModel::onRemoveFavorite,
            )
        }
    }
}
