package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.SessionState
import com.shaydev.rutayatesis.domain.repository.AuthRepository
import kotlinx.coroutines.flow.Flow

class ObserveSessionStateUseCase(
    private val authRepository: AuthRepository,
) {
    operator fun invoke(): Flow<SessionState> = authRepository.observeSessionState()
}
