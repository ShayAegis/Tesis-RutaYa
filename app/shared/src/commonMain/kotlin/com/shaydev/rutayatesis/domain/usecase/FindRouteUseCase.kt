package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.Place
import com.shaydev.rutayatesis.domain.model.Route
import com.shaydev.rutayatesis.domain.repository.RouteRepository

class FindRouteUseCase(
    private val routeRepository: RouteRepository,
) {
    suspend operator fun invoke(origin: Place, destination: Place, walkingDistance: Int): List<Route> {
        require(origin.id != destination.id) { "origin and destination must differ" }
        return routeRepository.findRoutes(origin, destination,walkingDistance)
    }
}
