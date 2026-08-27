package com.shaydev.rutayatesis.log

import platform.Foundation.NSLog

actual object AppLogger {
    actual fun error(tag: String, message: String, throwable: Throwable?) {
        val trace = throwable?.let { "\n${it.stackTraceToString()}" }.orEmpty()
        NSLog("[$tag] ERROR: $message$trace")
    }

    actual fun debug(tag: String, message: String) {
        NSLog("[$tag] DEBUG: $message")
    }
}
