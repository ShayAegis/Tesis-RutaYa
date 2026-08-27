package com.shaydev.rutayatesis.presentation.login

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import cafe.adriel.voyager.core.screen.Screen
import cafe.adriel.voyager.navigator.LocalNavigator
import cafe.adriel.voyager.navigator.currentOrThrow
import com.shaydev.rutayatesis.presentation.components.PasswordField
import com.shaydev.rutayatesis.presentation.components.PrimaryButton
import com.shaydev.rutayatesis.presentation.components.RutaYaTextField
import com.shaydev.rutayatesis.presentation.di.LocalAppGraph
import com.shaydev.rutayatesis.presentation.signup.SignUpScreen
import org.jetbrains.compose.resources.stringResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.ic_email
import rutaya_tesis.shared.generated.resources.ic_lock
import rutaya_tesis.shared.generated.resources.login_create_account
import rutaya_tesis.shared.generated.resources.login_email_placeholder
import rutaya_tesis.shared.generated.resources.login_password_placeholder
import rutaya_tesis.shared.generated.resources.login_signup
import rutaya_tesis.shared.generated.resources.login_subtitle
import rutaya_tesis.shared.generated.resources.login_title

class LoginScreen : Screen {

    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow
        val graph = LocalAppGraph.current
        val viewModel: LoginViewModel = viewModel(factory = graph.loginViewModelFactory())
        val emailInputState = rememberTextFieldState()
        val passwordInputState = rememberTextFieldState()
        val state by viewModel.state.collectAsStateWithLifecycle()

        LaunchedEffect(state.loginSucceeded) {
            if (state.loginSucceeded) {
                navigator.pop()
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.linearGradient(
                        colors = listOf(
                            MaterialTheme.colorScheme.surfaceVariant,
                            MaterialTheme.colorScheme.surface
                        ),
                        start = Offset.Zero,
                        end = Offset(0f, Float.POSITIVE_INFINITY)
                    )
                )
                .padding(WindowInsets.statusBars.asPaddingValues())
                .padding(20.dp),
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                stringResource(Res.string.login_title),
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.titleLarge
            )
            Spacer(Modifier.height(20.dp))
            Text(
                stringResource(Res.string.login_subtitle),
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(Modifier.height(40.dp))
            RutaYaTextField(
                emailInputState,
                placeholder = stringResource(Res.string.login_email_placeholder),
                leadingIcon = Res.drawable.ic_email,
                leadingIconDescription = "Ícono correo electrónico",
                isError = state.errorMessage != null,
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(Modifier.height(20.dp))
            PasswordField(
                state = passwordInputState,
                placeholder = stringResource(Res.string.login_password_placeholder),
                leadingIcon = Res.drawable.ic_lock,
                leadingIconDescription = "Ícono candado, campo contraseña",
                isError = state.errorMessage != null
            )
            if (state.errorMessage != null) {
                Spacer(Modifier.height(12.dp))
                Text(
                    state.errorMessage.orEmpty(),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Spacer(Modifier.height(20.dp))
            PrimaryButton(
                modifier = Modifier.fillMaxWidth(),
                label = if (state.isLoading) "Iniciando sesión..." else "Iniciar sesión",
                enabled = !state.isLoading,
                onClick = {
                    viewModel.onLoginClick(
                        email = emailInputState.text.toString(),
                        password = passwordInputState.text.toString(),
                    )
                },
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    stringResource(Res.string.login_create_account),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                )
                TextButton(onClick = {navigator.push(SignUpScreen())}) {
                    Text(
                        stringResource(Res.string.login_signup),
                        color = MaterialTheme.colorScheme.secondary,
                    )
                }
            }
        }
    }
}
