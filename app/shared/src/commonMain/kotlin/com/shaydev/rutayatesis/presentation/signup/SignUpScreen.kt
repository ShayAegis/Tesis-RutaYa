package com.shaydev.rutayatesis.presentation.signup

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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
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
import org.jetbrains.compose.resources.painterResource
import org.jetbrains.compose.resources.stringResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.ic_email
import rutaya_tesis.shared.generated.resources.ic_lock
import rutaya_tesis.shared.generated.resources.ic_user
import rutaya_tesis.shared.generated.resources.signup_login_label
import rutaya_tesis.shared.generated.resources.signup_login_textbtn

class SignUpScreen : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow
        val graph = LocalAppGraph.current
        val viewModel: SignUpViewModel = viewModel(factory = graph.signUpViewModelFactory())
        val nameTextState = rememberTextFieldState()
        val lastNameTextState = rememberTextFieldState()
        val emailTextState = rememberTextFieldState()
        val passwordTextState = rememberTextFieldState()
        val state by viewModel.state.collectAsStateWithLifecycle()

        LaunchedEffect(state.signUpSucceeded) {
            if (state.signUpSucceeded) {
                navigator.pop()
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(WindowInsets.statusBars.asPaddingValues())
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                "Crear Cuenta",
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center
            )
            Spacer(Modifier.height(20.dp))
            Text(
                "Crea tu cuenta para moverte por la ciudad",
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(Modifier.height(20.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    painter = painterResource(Res.drawable.ic_user),
                    contentDescription = "Ícono usuario nombre completo",
                    tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    modifier = Modifier.size(20.dp)
                )
                Spacer(Modifier.width(10.dp))
                Text(
                    "Nombre Completo",
                    color = MaterialTheme.colorScheme.primary,
                    style = MaterialTheme.typography.labelLarge
                )
            }
            Spacer(Modifier.height(22.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(0.4f)) {
                    Text(
                        "Nombres",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.padding(bottom = 10.dp)
                    )
                    RutaYaTextField(
                        nameTextState,
                        placeholder = "Ingrese sus nombres",
                        isError = state.nameErrorMessage != null,
                        modifier = Modifier.fillMaxWidth()
                    )
                    FieldErrorText(state.nameErrorMessage)
                }
                Spacer(modifier = Modifier.weight(weight = 0.1f))
                Column(modifier = Modifier.weight(0.4f)) {
                    Text(
                        "Apellidos",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.padding(bottom = 10.dp)
                    )
                    RutaYaTextField(
                        lastNameTextState,
                        placeholder = "Ingrese sus apellidos",
                        isError = state.lastNameErrorMessage != null,
                        modifier = Modifier.fillMaxWidth()
                    )
                    FieldErrorText(state.lastNameErrorMessage)
                }
            }

            Text(
                "Correo electrónico",
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.padding(vertical = 20.dp)
            )
            RutaYaTextField(
                emailTextState,
                leadingIcon = Res.drawable.ic_email,
                placeholder = "Ingrese su correo electrónico",
                isError = state.emailErrorMessage != null,
                modifier = Modifier.fillMaxWidth()
            )
            FieldErrorText(state.emailErrorMessage)
            Text(
                "Contraseña",
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.padding(vertical = 20.dp)
            )
            PasswordField(
                state = passwordTextState,
                leadingIcon = Res.drawable.ic_lock,
                leadingIconDescription = "Ícono candado, campo contraseña",
                placeholder = "Ingrese su contraseña",
                isError = state.passwordErrorMessage != null
            )
            FieldErrorText(state.passwordErrorMessage)
            if (state.errorMessage != null) {
                Spacer(Modifier.height(12.dp))
                Text(
                    state.errorMessage.orEmpty(),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Spacer(Modifier.height(40.dp))
            PrimaryButton(
                label = if (state.isLoading) "Creando cuenta..." else "Crear cuenta",
                enabled = !state.isLoading,
                onClick = {
                    viewModel.onSignUpClick(
                        name = nameTextState.text.toString(),
                        lastName = lastNameTextState.text.toString(),
                        email = emailTextState.text.toString(),
                        password = passwordTextState.text.toString(),
                    )
                },
                modifier = Modifier.fillMaxWidth()
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    stringResource(Res.string.signup_login_label),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                )
                TextButton(onClick = { navigator.pop() }) {
                    Text(
                        stringResource(Res.string.signup_login_textbtn),
                        color = MaterialTheme.colorScheme.secondary,
                    )
                }
            }
        }

    }
}

@Composable
private fun FieldErrorText(message: String?) {
    if (message != null) {
        Text(
            message,
            color = MaterialTheme.colorScheme.error,
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp)
        )
    }
}
