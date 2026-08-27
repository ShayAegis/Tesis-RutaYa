package com.shaydev.rutayatesis.data.repository

import com.shaydev.rutayatesis.BuildKonfig
import com.shaydev.rutayatesis.data.exceptions.AccountAlreadyExists
import com.shaydev.rutayatesis.data.exceptions.InvalidLoginCredentials
import com.shaydev.rutayatesis.data.exceptions.InvalidPasswordException
import com.shaydev.rutayatesis.data.exceptions.MissingFieldsException
import com.shaydev.rutayatesis.data.exceptions.UnexpectedSignUpError
import com.shaydev.rutayatesis.data.local.TokenStorage
import com.shaydev.rutayatesis.data.remote.dto.ErrorResponse
import com.shaydev.rutayatesis.data.remote.dto.LoginResponse
import com.shaydev.rutayatesis.data.remote.dto.RefreshTokenRequest
import com.shaydev.rutayatesis.data.remote.dto.UserDTO
import com.shaydev.rutayatesis.data.remote.dto.ValidationErrorResponse
import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.domain.model.User
import com.shaydev.rutayatesis.domain.repository.AuthRepository
import com.shaydev.rutayatesis.network.NetworkUtils
import io.ktor.client.call.body
import io.ktor.client.request.forms.FormDataContent
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.Parameters
import io.ktor.http.contentType
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ApiBackendOAuthRepository(
    private val network: NetworkUtils,
    private val tokenStorage: TokenStorage,
) : AuthRepository {
    // Unknown hasta que se resuelve la restauración de sesión al arrancar,
    // así la UI (ver FavoritesHomeScreen) no navega a LoginScreen ni muestra
    // contenido protegido mientras se lee el token persistido.
    private val state = MutableStateFlow<SessionState>(SessionState.Unknown)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    // En memoria para adjuntarlo a las peticiones sin leer el storage en cada
    // llamada. La copia persistente vive en tokenStorage (DataStore cifrado en
    // Android, Keychain en iOS) y sobrevive al cierre de la app.
    private var accessToken: String? = null

    init {
        restoreSession()
    }

    override fun observeSessionState(): Flow<SessionState> = state.asStateFlow()

    override suspend fun login(email: String, password: String): Result<Unit> = runCatching {
        val url = "${BuildKonfig.API_BASE_URL}/login"
        val apiResponse = network.httpClient.post(url) {
            setBody(
                FormDataContent(
                    Parameters.build {
                        append("username", email)
                        append("password", password)
                    }
                )
            )
        }
        if (apiResponse.status.value != 200) {
            throw InvalidLoginCredentials("Correo o contraseña incorrectos. Por favor, inténtalo de nuevo.")
        }
        val loginResponse = apiResponse.body<LoginResponse>()
        accessToken = loginResponse.accessToken
        tokenStorage.saveToken(loginResponse.accessToken)
        tokenStorage.saveRefreshToken(loginResponse.refreshToken)
        state.value = SessionState.LoggedIn
    }

    override suspend fun signup(user: User) {
        val url = "${BuildKonfig.API_BASE_URL}/usuarios/"
        val apiResponse = network.httpClient.post(url) {
            contentType(ContentType.Application.Json)
            setBody(
                UserDTO(
                    nombres = user.name,
                    apellidos = user.lastName,
                    email = user.email,
                    contrasenia = user.password
                )
            )
        }
        when (apiResponse.status.value) {
            201 -> {}
            400 -> {
                val errorResponse = apiResponse.body<ErrorResponse>()
                throw InvalidPasswordException(errorResponse.detail)
            }

            409 -> throw (AccountAlreadyExists("Este correo electrónico ya fue registrado"))
            422 -> {
                val validationError = apiResponse.body<ValidationErrorResponse>()
                val missingFields =
                    validationError.detail.mapNotNull { it.loc.lastOrNull() }.toSet()
                throw MissingFieldsException(
                    fields = missingFields,
                    message = "Por favor completa los campos requeridos."
                )
            }

            else -> {
                throw UnexpectedSignUpError("Ha ocurrido un error inesperado al crear el usuario")
            }
        }

    }

    override suspend fun logout() {
        accessToken = null
        tokenStorage.clearToken()
        state.value = SessionState.LoggedOut
    }

    override suspend fun getAccessToken(): String? = accessToken ?: tokenStorage.getToken()

    override suspend fun refreshSession(): Boolean {
        val storedRefreshToken = tokenStorage.getRefreshToken() ?: return false
        val url = "${BuildKonfig.API_BASE_URL}/refresh"
        val response = network.httpClient.post(url) {
            contentType(ContentType.Application.Json)
            setBody(RefreshTokenRequest(storedRefreshToken))
        }
        if (response.status.value != 200) return false
        val token = response.body<LoginResponse>()
        accessToken = token.accessToken
        tokenStorage.saveToken(token.accessToken)
        tokenStorage.saveRefreshToken(token.refreshToken)
        return true
    }

    private fun restoreSession() {
        scope.launch {
            val storedToken = tokenStorage.getToken()
            accessToken = storedToken
            state.value = if (storedToken != null) SessionState.LoggedIn else SessionState.LoggedOut
        }
    }
}
