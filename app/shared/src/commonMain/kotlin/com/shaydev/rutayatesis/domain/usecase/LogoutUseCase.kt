package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.repository.AuthRepository

class LogoutUseCase(
    private val authRepository: AuthRepository,
) {
    suspend operator fun invoke() = authRepository.logout()
}
