package com.shaydev.rutayatesis.data.repository

interface AppCheckTokenProvider {
    suspend fun getAppCheckProvider(): String?
}

expect fun createAppCheckTokenProvider(): AppCheckTokenProvider