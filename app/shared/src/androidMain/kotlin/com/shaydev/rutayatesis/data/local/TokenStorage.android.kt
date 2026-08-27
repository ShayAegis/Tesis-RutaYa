package com.shaydev.rutayatesis.data.local

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.shaydev.rutayatesis.AndroidContextHolder
import kotlinx.coroutines.flow.first
import java.security.KeyStore
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

private val Context.tokenDataStore: DataStore<Preferences> by preferencesDataStore(name = "secure_token_store")

private const val ANDROID_KEYSTORE = "AndroidKeyStore"
private const val KEY_ALIAS = "rutaya_auth_token_key"
private const val TRANSFORMATION = "AES/GCM/NoPadding"
private const val GCM_TAG_LENGTH_BITS = 128

/**
 * DataStore de preferencias cuyo valor se cifra/descifra con una clave AES-256-GCM
 * respaldada por el Android Keystore, de forma que el token nunca queda en texto
 * plano en disco (equivalente al "EncryptedDataStore" que no existe como API oficial
 * de Jetpack; EncryptedSharedPreferences es su análogo pero DataStore es el reemplazo
 * recomendado de SharedPreferences).
 */
class EncryptedDataStoreTokenStorage(context: Context) : TokenStorage {
    private val appContext = context.applicationContext
    private val tokenKey = stringPreferencesKey("access_token")
    private val refreshTokenKey = stringPreferencesKey("refresh_token")

    override suspend fun saveToken(token: String) {
        val encrypted = encrypt(token)
        appContext.tokenDataStore.edit { prefs -> prefs[tokenKey] = encrypted }
    }

    override suspend fun getToken(): String? {
        val stored = appContext.tokenDataStore.data.first()[tokenKey] ?: return null
        return decrypt(stored)
    }

    override suspend fun saveRefreshToken(token: String) {
        val encrypted = encrypt(token)
        appContext.tokenDataStore.edit { prefs -> prefs[refreshTokenKey] = encrypted }
    }

    override suspend fun getRefreshToken(): String? {
        val stored = appContext.tokenDataStore.data.first()[refreshTokenKey] ?: return null
        return decrypt(stored)
    }

    override suspend fun clearToken() {
        appContext.tokenDataStore.edit { prefs ->
            prefs.remove(tokenKey)
            prefs.remove(refreshTokenKey)
        }
    }

    private fun encrypt(plainText: String): String {
        val cipher = Cipher.getInstance(TRANSFORMATION).apply {
            init(Cipher.ENCRYPT_MODE, getOrCreateSecretKey())
        }
        val cipherBytes = cipher.doFinal(plainText.toByteArray(Charsets.UTF_8))
        val iv = Base64.getEncoder().encodeToString(cipher.iv)
        val payload = Base64.getEncoder().encodeToString(cipherBytes)
        return "$iv:$payload"
    }

    private fun decrypt(stored: String): String {
        val (ivB64, payloadB64) = stored.split(":", limit = 2)
        val iv = Base64.getDecoder().decode(ivB64)
        val cipherBytes = Base64.getDecoder().decode(payloadB64)
        val cipher = Cipher.getInstance(TRANSFORMATION).apply {
            init(Cipher.DECRYPT_MODE, getOrCreateSecretKey(), GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv))
        }
        return String(cipher.doFinal(cipherBytes), Charsets.UTF_8)
    }

    private fun getOrCreateSecretKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        (keyStore.getEntry(KEY_ALIAS, null) as? KeyStore.SecretKeyEntry)?.let { return it.secretKey }

        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .build()
        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }
}

actual fun createTokenStorage(): TokenStorage = EncryptedDataStoreTokenStorage(AndroidContextHolder.appContext)
