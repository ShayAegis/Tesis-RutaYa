package com.shaydev.rutayatesis.data.local

/**
 * Persiste el access token y el refresh token de sesión de forma segura.
 * Android: DataStore con el valor cifrado vía Android Keystore.
 * iOS: Keychain.
 */
interface TokenStorage {
    suspend fun saveToken(token: String)
    suspend fun getToken(): String?
    suspend fun saveRefreshToken(token: String)
    suspend fun getRefreshToken(): String?
    suspend fun clearToken()
}

expect fun createTokenStorage(): TokenStorage
