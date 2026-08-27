package com.shaydev.rutayatesis.presentation.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shaydev.rutayatesis.data.exceptions.InvalidLoginCredentials
import com.shaydev.rutayatesis.domain.usecase.LoginUseCase
import com.shaydev.rutayatesis.log.AppLogger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class LoginUiState(
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val loginSucceeded: Boolean = false,
)

class LoginViewModel(
    private val login: LoginUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state.asStateFlow()

    fun onLoginClick(email: String, password: String) {
        _state.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            login(email, password)
                .onSuccess {
                    _state.update { it.copy(isLoading = false, loginSucceeded = true) }
                }
                .onFailure { error ->
                    AppLogger.error(TAG, "Error al iniciar sesión", error)
                    val message = (error as? InvalidLoginCredentials)?.message
                        ?: "No se pudo iniciar sesión. Intenta nuevamente."
                    _state.update { it.copy(isLoading = false, errorMessage = message) }
                }
        }
    }

    companion object {
        private const val TAG = "LoginViewModel"
    }
}
