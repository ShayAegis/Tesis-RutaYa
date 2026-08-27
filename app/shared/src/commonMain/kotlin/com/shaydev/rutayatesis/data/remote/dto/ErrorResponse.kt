package com.shaydev.rutayatesis.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ErrorResponse(
    val detail: String = "",
)
