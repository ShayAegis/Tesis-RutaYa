package com.shaydev.rutayatesis.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class UserDTO(
    val nombres: String,
    val apellidos: String,
    val email: String,
    val contrasenia: String
)
