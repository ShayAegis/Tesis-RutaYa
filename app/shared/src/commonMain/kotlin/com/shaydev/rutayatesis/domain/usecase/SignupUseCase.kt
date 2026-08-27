package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.User
import com.shaydev.rutayatesis.domain.repository.AuthRepository

class SignupUseCase(
    private val authRepository: AuthRepository,
) {
    suspend operator fun invoke(user: User) = authRepository.signup(user)
}
