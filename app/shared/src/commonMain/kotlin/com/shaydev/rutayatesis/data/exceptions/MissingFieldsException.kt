package com.shaydev.rutayatesis.data.exceptions

class MissingFieldsException(
    val fields: Set<String>,
    message: String,
) : Exception(message)
