package com.shaydev.rutayatesis.presentation.toast

import android.widget.Toast
import com.shaydev.rutayatesis.AndroidContextHolder

actual object ToastPresenter {
    actual fun show(message: String) {
        Toast.makeText(AndroidContextHolder.appContext, message, Toast.LENGTH_SHORT).show()
    }
}
