---
name: api-rutaya
description: Contexto sobre la API del proyecto RutaYa. Úsalo cuando se hable de la API, el backend, los endpoints, las rutas HTTP, o cómo el firmware/rastreador debe comunicarse con el servidor.
---

Cuando se hable de la API, revisa el código del backend para entender su estructura antes de responder o proponer cambios en el firmware:

/home/shaydev/Development/Proyectos/Tesis-RutaYa api

Pasos:
1. Explora el directorio con Glob/Grep para identificar el framework usado, la estructura de rutas/controladores y el archivo principal de entrada
2. Revisa los endpoints relevantes: métodos HTTP, parámetros esperados, formato de los payloads (JSON), y validaciones
3. Si la consulta es sobre integración con el firmware, verifica que los datos que este envía (formato, campos, tipos) coincidan con lo que la API espera recibir
4. Señala explícitamente cualquier discrepancia entre lo que hace el firmware y lo que la API valida o espera
