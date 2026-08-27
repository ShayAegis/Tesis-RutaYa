package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.Route
import kotlin.time.Clock
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Instant

class GetRouteArrivalTimeUseCase(
    private val clock: Clock = Clock.System,
) {
    operator fun invoke(route: Route): Instant = clock.now() + route.etaSeconds.seconds
}
