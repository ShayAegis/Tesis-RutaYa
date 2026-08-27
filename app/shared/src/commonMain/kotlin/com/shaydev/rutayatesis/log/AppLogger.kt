package com.shaydev.rutayatesis.log

expect object AppLogger {
    fun error(tag: String, message: String, throwable: Throwable? = null)
    fun debug(tag: String, message: String)
}
