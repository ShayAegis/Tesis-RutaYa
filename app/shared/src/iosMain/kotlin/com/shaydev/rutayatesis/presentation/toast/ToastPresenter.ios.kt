package com.shaydev.rutayatesis.presentation.toast

import kotlinx.cinterop.ExperimentalForeignApi
import platform.Foundation.NSTimer
import platform.UIKit.UIAlertController
import platform.UIKit.UIAlertControllerStyleAlert
import platform.UIKit.UIApplication

private const val TOAST_DURATION_SECONDS = 1.5

// iOS no tiene un widget de Toast nativo; un UIAlertController sin botones que
// se autodescarta es el equivalente más cercano sin arrastrar una dependencia extra.
@OptIn(ExperimentalForeignApi::class)
actual object ToastPresenter {
    actual fun show(message: String) {
        val rootViewController = UIApplication.sharedApplication.keyWindow?.rootViewController
            ?: return
        val alert = UIAlertController.alertControllerWithTitle(
            title = null,
            message = message,
            preferredStyle = UIAlertControllerStyleAlert,
        )
        rootViewController.presentViewController(alert, animated = true, completion = null)
        NSTimer.scheduledTimerWithTimeInterval(TOAST_DURATION_SECONDS, repeats = false) {
            alert.dismissViewControllerAnimated(true, completion = null)
        }
    }
}
