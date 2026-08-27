package com.shaydev.rutayatesis.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ValidationErrorResponse(
    val detail: List<ValidationErrorDetail> = emptyList(),
)

@Serializable
data class ValidationErrorDetail(
    val loc: List<String> = emptyList(),
    val msg: String = "",
)
