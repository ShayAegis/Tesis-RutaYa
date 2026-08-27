package com.shaydev.rutayatesis.presentation.signup

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shaydev.rutayatesis.data.exceptions.AccountAlreadyExists
import com.shaydev.rutayatesis.data.exceptions.InvalidPasswordException
import com.shaydev.rutayatesis.data.exceptions.MissingFieldsException
import com.shaydev.rutayatesis.domain.model.User
import com.shaydev.rutayatesis.domain.usecase.SignupUseCase
import com.shaydev.rutayatesis.log.AppLogger
import com.shaydev.rutayatesis.presentation.toast.ToastPresenter
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SignUpUiState(
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val signUpSucceeded: Boolean = false,
    val nameErrorMessage: String? = null,
    val lastNameErrorMessage: String? = null,
    val emailErrorMessage: String? = null,
    val passwordErrorMessage: String? = null,
)

class SignUpViewModel(
    private val signup: SignupUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(SignUpUiState())
    val state: StateFlow<SignUpUiState> = _state.asStateFlow()

    fun onSignUpClick(name: String, lastName: String, email: String, password: String) {
        _state.update {
            it.copy(
                isLoading = true,
                errorMessage = null,
                nameErrorMessage = null,
                lastNameErrorMessage = null,
                emailErrorMessage = null,
                passwordErrorMessage = null,
            )
        }
        viewModelScope.launch {
            runCatching { signup(User(name, lastName, email, password)) }
                .onSuccess {
                    ToastPresenter.show("Usuario creado exitosamente")
                    _state.update { it.copy(isLoading = false, signUpSucceeded = true) }
                }
                .onFailure { error ->
                    AppLogger.error(TAG, "Error al crear la cuenta", error)
                    _state.update { current ->
                        when (error) {
                            is MissingFieldsException -> current.copy(
                                isLoading = false,
                                nameErrorMessage = REQUIRED_FIELD_MESSAGE.takeIf { FIELD_NAME in error.fields },
                                lastNameErrorMessage = REQUIRED_FIELD_MESSAGE.takeIf { FIELD_LAST_NAME in error.fields },
                                emailErrorMessage = REQUIRED_FIELD_MESSAGE.takeIf { FIELD_EMAIL in error.fields },
                                passwordErrorMessage = REQUIRED_FIELD_MESSAGE.takeIf { FIELD_PASSWORD in error.fields },
                            )
                            is AccountAlreadyExists -> current.copy(
                                isLoading = false,
                                emailErrorMessage = error.message,
                            )
                            is InvalidPasswordException -> current.copy(
                                isLoading = false,
                                passwordErrorMessage = error.message,
                            )
                            else -> current.copy(
                                isLoading = false,
                                errorMessage = "No se pudo crear la cuenta. Intenta nuevamente.",
                            )
                        }
                    }
                }
        }
    }

    companion object {
        private const val TAG = "SignUpViewModel"
        private const val FIELD_NAME = "nombres"
        private const val FIELD_LAST_NAME = "apellidos"
        private const val FIELD_EMAIL = "email"
        private const val FIELD_PASSWORD = "contrasenia"
        private const val REQUIRED_FIELD_MESSAGE = "Este campo es requerido"
    }
}
