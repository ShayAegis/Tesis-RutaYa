package com.shaydev.rutayatesis.data.location

import com.shaydev.rutayatesis.domain.model.Point

expect suspend fun getCurrentLocation(): Point?
