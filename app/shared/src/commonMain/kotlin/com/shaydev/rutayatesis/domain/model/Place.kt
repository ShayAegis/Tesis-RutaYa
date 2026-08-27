package com.shaydev.rutayatesis.domain.model

data class Place(
    val id: String,
    val name: String,
    val location: Point,
    val matches_offset: Int
)
