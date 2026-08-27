package com.shaydev.rutayatesis.network

import com.shaydev.rutayatesis.data.repository.AppCheckTokenProvider
import com.shaydev.rutayatesis.data.repository.createAppCheckTokenProvider
import io.ktor.client.HttpClient
import io.ktor.client.plugins.api.createClientPlugin
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.sse.SSE
import io.ktor.http.ContentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

object NetworkUtils {
    private val appCheckTokenProvider: AppCheckTokenProvider = createAppCheckTokenProvider()
    private val firebaseAppCheckInterceptor = createClientPlugin("FirebaseAppCheckInterceptor") {
        onRequest { request, _ ->
            val token = appCheckTokenProvider.getAppCheckProvider()
            if (!token.isNullOrEmpty()) {
                request.headers.append("X-Firebase-AppCheck", token)
            }
        }
    }
    val httpClient = HttpClient{
        install(ContentNegotiation){
            json(json = Json{ ignoreUnknownKeys=true }, contentType = ContentType.Application.Any)
        }
        install(SSE)
        install(firebaseAppCheckInterceptor)
    }

}

