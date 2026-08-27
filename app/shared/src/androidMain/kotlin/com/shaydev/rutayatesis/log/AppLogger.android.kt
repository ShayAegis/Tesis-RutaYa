package com.shaydev.rutayatesis.log

import android.util.Log

actual object AppLogger {
    actual fun error(tag: String, message: String, throwable: Throwable?) {
        Log.e(tag, message, throwable)
    }

    actual fun debug(tag: String, message: String) {
        Log.d(tag, message)
    }
}
