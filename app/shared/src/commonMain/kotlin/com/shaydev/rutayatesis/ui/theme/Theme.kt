import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import com.shaydev.rutayatesis.ui.theme.DarkColorScheme
import com.shaydev.rutayatesis.ui.theme.RutaYaTypography

@Composable
fun RutaYaTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else DarkColorScheme,
        typography = RutaYaTypography,
        content = content,
    )
}
