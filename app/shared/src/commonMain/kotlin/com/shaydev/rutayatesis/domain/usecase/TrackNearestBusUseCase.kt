package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.NearestBus
import com.shaydev.rutayatesis.domain.model.Point
import com.shaydev.rutayatesis.domain.model.Route
import com.shaydev.rutayatesis.domain.repository.RouteRepository

class TrackNearestBusUseCase(
    private val routeRepository: RouteRepository,
) {
    suspend operator fun invoke(route: Route, origin: Point): NearestBus? =
        routeRepository.findNearestBus(route.code, origin, route.returnWay)
}
