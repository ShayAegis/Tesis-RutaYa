package com.shaydev.rutayatesis.data.local

import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.addressOf
import kotlinx.cinterop.alloc
import kotlinx.cinterop.convert
import kotlinx.cinterop.memScoped
import kotlinx.cinterop.ptr
import kotlinx.cinterop.usePinned
import kotlinx.cinterop.value
import platform.CoreFoundation.CFDictionaryCreateMutable
import platform.CoreFoundation.CFDictionarySetValue
import platform.CoreFoundation.CFMutableDictionaryRef
import platform.CoreFoundation.CFTypeRefVar
import platform.CoreFoundation.kCFTypeDictionaryKeyCallBacks
import platform.CoreFoundation.kCFTypeDictionaryValueCallBacks
import platform.Foundation.CFBridgingRelease
import platform.Foundation.CFBridgingRetain
import platform.Foundation.NSData
import platform.Foundation.create
import platform.Security.SecItemAdd
import platform.Security.SecItemCopyMatching
import platform.Security.SecItemDelete
import platform.Security.errSecSuccess
import platform.Security.kSecAttrAccessible
import platform.Security.kSecAttrAccessibleAfterFirstUnlock
import platform.Security.kSecAttrAccount
import platform.Security.kSecAttrService
import platform.Security.kSecClass
import platform.Security.kSecClassGenericPassword
import platform.Security.kSecMatchLimit
import platform.Security.kSecMatchLimitOne
import platform.Security.kSecReturnData
import platform.Security.kSecValueData
import platform.posix.memcpy

private const val SERVICE = "com.shadev.rutayatesis.auth"
private const val ACCESS_TOKEN_ACCOUNT = "access_token"
private const val REFRESH_TOKEN_ACCOUNT = "refresh_token"

/**
 * Guarda el token en el Keychain de iOS, el equivalente nativo al DataStore
 * cifrado de Android: el sistema operativo se encarga del cifrado en reposo.
 */
@OptIn(ExperimentalForeignApi::class)
class KeychainTokenStorage : TokenStorage {

    override suspend fun saveToken(token: String) = savePassword(ACCESS_TOKEN_ACCOUNT, token)

    override suspend fun getToken(): String? = getPassword(ACCESS_TOKEN_ACCOUNT)

    override suspend fun saveRefreshToken(token: String) = savePassword(REFRESH_TOKEN_ACCOUNT, token)

    override suspend fun getRefreshToken(): String? = getPassword(REFRESH_TOKEN_ACCOUNT)

    override suspend fun clearToken() {
        SecItemDelete(baseQuery(ACCESS_TOKEN_ACCOUNT))
        SecItemDelete(baseQuery(REFRESH_TOKEN_ACCOUNT))
    }

    private fun savePassword(account: String, token: String) {
        val data = token.toNSData()
        SecItemDelete(baseQuery(account))
        val attributes = baseQuery(account)
        CFDictionarySetValue(attributes, kSecValueData, CFBridgingRetain(data))
        CFDictionarySetValue(attributes, kSecAttrAccessible, kSecAttrAccessibleAfterFirstUnlock)
        SecItemAdd(attributes, null)
    }

    private fun getPassword(account: String): String? = memScoped {
        val query = baseQuery(account)
        CFDictionarySetValue(query, kSecReturnData, CFBridgingRetain(true))
        CFDictionarySetValue(query, kSecMatchLimit, kSecMatchLimitOne)
        val result = alloc<CFTypeRefVar>()
        val status = SecItemCopyMatching(query, result.ptr)
        if (status != errSecSuccess) return@memScoped null
        val data = CFBridgingRelease(result.value) as? NSData ?: return@memScoped null
        data.toKString()
    }

    private fun baseQuery(account: String): CFMutableDictionaryRef? {
        val dict = CFDictionaryCreateMutable(
            null,
            0,
            kCFTypeDictionaryKeyCallBacks.ptr,
            kCFTypeDictionaryValueCallBacks.ptr,
        )
        CFDictionarySetValue(dict, kSecClass, kSecClassGenericPassword)
        CFDictionarySetValue(dict, kSecAttrService, CFBridgingRetain(SERVICE))
        CFDictionarySetValue(dict, kSecAttrAccount, CFBridgingRetain(account))
        return dict
    }
}

@OptIn(ExperimentalForeignApi::class, kotlinx.cinterop.BetaInteropApi::class)
private fun String.toNSData(): NSData {
    val bytes = encodeToByteArray()
    if (bytes.isEmpty()) return NSData()
    return bytes.usePinned { pinned ->
        NSData.create(bytes = pinned.addressOf(0), length = bytes.size.convert())
    }
}

@OptIn(ExperimentalForeignApi::class, kotlinx.cinterop.BetaInteropApi::class)
private fun NSData.toKString(): String {
    val size = length.toInt()
    if (size == 0) return ""
    val result = ByteArray(size)
    result.usePinned { pinned ->
        memcpy(pinned.addressOf(0), bytes, size.convert())
    }
    return result.decodeToString()
}

actual fun createTokenStorage(): TokenStorage = KeychainTokenStorage()
