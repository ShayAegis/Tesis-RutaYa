package com.shaydev.rutayatesis.domain.repository

import com.shaydev.rutayatesis.domain.model.NearestBus
import com.shaydev.rutayatesis.domain.model.Place
import com.shaydev.rutayatesis.domain.model.Point
import com.shaydev.rutayatesis.domain.model.Route

interface RouteRepository {
    suspend fun findRoutes(origin: Place, destination: Place, walkingDistance: Int): List<Route>
    suspend fun findNearestBus(routeCode: String, origin: Point, returnWay: Boolean): NearestBus?
}
