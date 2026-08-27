package com.shaydev.rutayatesis.presentation.util

import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import kotlin.time.Instant

fun Instant.toAmPmLabel(timeZone: TimeZone = TimeZone.currentSystemDefault()): String {
    val localTime = toLocalDateTime(timeZone)
    val period = if (localTime.hour < 12) "a. m." else "p. m."
    val hour12 = when (val hour = localTime.hour % 12) {
        0 -> 12
        else -> hour
    }
    val minute = localTime.minute.toString().padStart(2, '0')
    return "$hour12:$minute $period"
}
