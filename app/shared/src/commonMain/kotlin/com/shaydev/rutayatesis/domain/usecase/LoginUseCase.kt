package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.repository.AuthRepository

class LoginUseCase(
    private val authRepository: AuthRepository,
) {
    suspend operator fun invoke(email: String, password: String): Result<Unit> =
        authRepository.login(email, password)
}
