package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.repository.AuthRepository

class GetAccessTokenUseCase(
    private val authRepository: AuthRepository,
) {
    suspend operator fun invoke(): String? = authRepository.getAccessToken()
}
