package com.shaydev.rutayatesis.data.repository

class IosAppCheckTokenProvider : AppCheckTokenProvider {
    override suspend fun getAppCheckProvider(): String? {
        // Retorna null por defecto hasta configurar Firebase en el target de iOS (Xcode)
        return null
    }
}

actual fun createAppCheckTokenProvider(): AppCheckTokenProvider = IosAppCheckTokenProvider()
