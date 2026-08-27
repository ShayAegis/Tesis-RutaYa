package com.shaydev.rutayatesis.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import org.jetbrains.compose.resources.painterResource
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.ic_bus


@Composable
fun BusNumberBadge(busFound: Boolean, busNumber: Int?) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(5.dp))
            .background(
                if (!busFound)
                    MaterialTheme.colorScheme.onSurface
                else MaterialTheme.colorScheme.secondary
            )
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                painter = painterResource(Res.drawable.ic_bus),
                modifier = Modifier.size(20.dp)
                    .padding(start = 5.dp),
                contentDescription = "Ícono bus número bus",
                tint = if (!busFound)
                    MaterialTheme.colorScheme.inverseOnSurface
                else MaterialTheme.colorScheme.onSurface,
            )
            Text(
                if (!busFound) "--"
                else busNumber.toString(),
                color = if (!busFound)
                    MaterialTheme.colorScheme.inverseOnSurface
                else MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.padding(end = 5.dp),
                style = MaterialTheme.typography.labelSmallEmphasized
            )
        }
    }
}