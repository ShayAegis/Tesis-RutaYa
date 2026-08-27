package com.shaydev.rutayatesis.domain.model

sealed interface PlaceField {
    data object Origin : PlaceField
    data object Destination : PlaceField
}
