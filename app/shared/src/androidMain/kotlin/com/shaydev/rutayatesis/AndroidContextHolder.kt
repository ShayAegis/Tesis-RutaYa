package com.shaydev.rutayatesis

import android.content.Context

/**
 * Referencia al Application Context inicializada desde la Application de androidApp.
 * Necesaria porque el módulo shared no puede recibir Context vía constructor
 * sin romper el patrón expect/actual usado en el resto del proyecto.
 */
object AndroidContextHolder {
    lateinit var appContext: Context
}
