package com.shaydev.rutayatesis.domain.repository

import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.domain.model.User
import kotlinx.coroutines.flow.Flow

interface AuthRepository {
    fun observeSessionState(): Flow<SessionState>
    suspend fun login(email: String, password: String): Result<Unit>
    suspend fun signup(user: User): Unit
    suspend fun logout()
    suspend fun getAccessToken(): String?
    suspend fun refreshSession(): Boolean
}
