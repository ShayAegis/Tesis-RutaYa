package com.shaydev.rutayatesis

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform