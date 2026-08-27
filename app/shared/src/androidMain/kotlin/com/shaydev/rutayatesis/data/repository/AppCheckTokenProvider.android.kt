package com.shaydev.rutayatesis.data.repository

import com.google.firebase.appcheck.FirebaseAppCheck
import kotlinx.coroutines.tasks.await

class AndroidAppCheckTokenProvider : AppCheckTokenProvider {
    override suspend fun getAppCheckProvider(): String? {
        return try {
            val result = FirebaseAppCheck.getInstance().getAppCheckToken(false).await()
            result.token
        } catch (e: Exception) {
            null
        }
    }
}

actual fun createAppCheckTokenProvider(): AppCheckTokenProvider = AndroidAppCheckTokenProvider()