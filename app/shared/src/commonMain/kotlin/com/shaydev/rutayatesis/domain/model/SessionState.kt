package com.shaydev.rutayatesis.domain.model

sealed interface SessionState {
    data object Unknown : SessionState
    data object LoggedOut : SessionState
    data object LoggedIn : SessionState
}
