package com.shaydev.rutayatesis.presentation.di

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.CreationExtras
import com.shaydev.rutayatesis.data.local.createFavoriteRouteIdsCache
import com.shaydev.rutayatesis.data.local.createTokenStorage
import com.shaydev.rutayatesis.data.repository.GoogleBackendProxyPlacesRepository
import com.shaydev.rutayatesis.data.repository.ApiBackendBusRepository
import com.shaydev.rutayatesis.data.repository.ApiBackendOAuthRepository
import com.shaydev.rutayatesis.data.repository.ApiBackendFavoritesRepository
import com.shaydev.rutayatesis.data.repository.ApiBackendRouteRepository
import com.shaydev.rutayatesis.domain.repository.AuthRepository
import com.shaydev.rutayatesis.domain.repository.BusRepository
import com.shaydev.rutayatesis.domain.repository.FavoritesRepository
import com.shaydev.rutayatesis.domain.repository.PlacesRepository
import com.shaydev.rutayatesis.domain.repository.RouteRepository
import com.shaydev.rutayatesis.domain.usecase.AddFavoriteUseCase
import com.shaydev.rutayatesis.domain.usecase.FindRouteUseCase
import com.shaydev.rutayatesis.domain.usecase.GetAccessTokenUseCase
import com.shaydev.rutayatesis.domain.usecase.GetFavoritesUseCase
import com.shaydev.rutayatesis.domain.usecase.GetPlaceAutocompleteUseCase
import com.shaydev.rutayatesis.domain.usecase.GetRouteArrivalTimeUseCase
import com.shaydev.rutayatesis.domain.usecase.LoginUseCase
import com.shaydev.rutayatesis.domain.usecase.LogoutUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveBusLocationUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveFavoriteRouteIdsUseCase
import com.shaydev.rutayatesis.domain.usecase.ObserveSessionStateUseCase
import com.shaydev.rutayatesis.domain.usecase.RemoveFavoriteUseCase
import com.shaydev.rutayatesis.domain.usecase.SignupUseCase
import com.shaydev.rutayatesis.domain.usecase.TrackNearestBusUseCase
import com.shaydev.rutayatesis.network.NetworkUtils
import com.shaydev.rutayatesis.presentation.favorites.FavoritesViewModel
import com.shaydev.rutayatesis.presentation.home.HomeViewModel
import com.shaydev.rutayatesis.presentation.login.LoginViewModel
import com.shaydev.rutayatesis.presentation.signup.SignUpViewModel
import kotlin.reflect.KClass

class AppGraph(
    val routeRepository: RouteRepository = ApiBackendRouteRepository(NetworkUtils),
    val authRepository: AuthRepository = ApiBackendOAuthRepository(NetworkUtils, createTokenStorage()),
    val favoritesRepository: FavoritesRepository = ApiBackendFavoritesRepository(
        NetworkUtils,
        authRepository,
        createFavoriteRouteIdsCache(),
    ),
    val placesRepository: PlacesRepository = GoogleBackendProxyPlacesRepository(NetworkUtils),
    val busRepository: BusRepository = ApiBackendBusRepository(NetworkUtils),
) {
    val findRouteUseCase: FindRouteUseCase = FindRouteUseCase(routeRepository)
    val getRouteArrivalTimeUseCase: GetRouteArrivalTimeUseCase = GetRouteArrivalTimeUseCase()
    val trackNearestBusUseCase: TrackNearestBusUseCase = TrackNearestBusUseCase(routeRepository)
    val observeBusLocationUseCase: ObserveBusLocationUseCase = ObserveBusLocationUseCase(busRepository)
    val getFavoritesUseCase: GetFavoritesUseCase = GetFavoritesUseCase(favoritesRepository)
    val getPlaceAutocompleteUseCase: GetPlaceAutocompleteUseCase = GetPlaceAutocompleteUseCase(placesRepository)
    val removeFavoriteUseCase: RemoveFavoriteUseCase = RemoveFavoriteUseCase(favoritesRepository)
    val addFavoriteUseCase: AddFavoriteUseCase = AddFavoriteUseCase(favoritesRepository)
    val observeFavoriteRouteIdsUseCase: ObserveFavoriteRouteIdsUseCase = ObserveFavoriteRouteIdsUseCase(favoritesRepository)
    val observeSessionStateUseCase: ObserveSessionStateUseCase = ObserveSessionStateUseCase(authRepository)
    val loginUseCase: LoginUseCase = LoginUseCase(authRepository)
    val signupUseCase: SignupUseCase = SignupUseCase(authRepository)
    val logoutUseCase: LogoutUseCase = LogoutUseCase(authRepository)
    val getAccessTokenUseCase: GetAccessTokenUseCase = GetAccessTokenUseCase(authRepository)

    fun homeViewModelFactory(): ViewModelProvider.Factory =
        object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: KClass<T>, extras: CreationExtras): T {
                require(modelClass == HomeViewModel::class) {
                    "Unknown ViewModel class: $modelClass"
                }
                return HomeViewModel(
                    observeSessionStateUseCase,
                    findRouteUseCase,
                    getPlaceAutocompleteUseCase,
                    getRouteArrivalTimeUseCase,
                    trackNearestBusUseCase,
                    observeBusLocationUseCase,
                    addFavoriteUseCase,
                    removeFavoriteUseCase,
                    observeFavoriteRouteIdsUseCase,
                    getAccessTokenUseCase,
                    logoutUseCase,
                ) as T
            }
        }

    fun favoritesViewModelFactory(): ViewModelProvider.Factory =
        object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: KClass<T>, extras: CreationExtras): T {
                require(modelClass == FavoritesViewModel::class) {
                    "Unknown ViewModel class: $modelClass"
                }
                return FavoritesViewModel(
                    observeSessionStateUseCase,
                    removeFavoriteUseCase,
                    getFavoritesUseCase,
                    getAccessTokenUseCase,
                    logoutUseCase,
                ) as T
            }
        }

    fun loginViewModelFactory(): ViewModelProvider.Factory =
        object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: KClass<T>, extras: CreationExtras): T {
                require(modelClass == LoginViewModel::class) {
                    "Unknown ViewModel class: $modelClass"
                }
                return LoginViewModel(loginUseCase) as T
            }
        }

    fun signUpViewModelFactory(): ViewModelProvider.Factory =
        object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: KClass<T>, extras: CreationExtras): T {
                require(modelClass == SignUpViewModel::class) {
                    "Unknown ViewModel class: $modelClass"
                }
                return SignUpViewModel(signupUseCase) as T
            }
        }
}
