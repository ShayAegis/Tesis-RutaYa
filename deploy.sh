#!/bin/bash

set -e 

echo -e "\e[1;33m[INFO] Levantando contenedores de Docker\e[0m"
docker compose up -d --build
echo -e "\e[1;32m[SUCCESS] Contenedores levantados exitosamente\e[0m"

echo -e "\e[1;33m[INFO] Ejecutando migraciones de Django\e[0m"
docker compose exec webapp python3 manage.py makemigrations && \
docker compose exec webapp python3 manage.py migrate
echo -e "\e[1;32m[SUCCESS] Migraciones ejecutadas exitosamente\e[0m"

echo -e "Es la primera vez que despliegas? \e[1;31m(Si no es la primera vez, responder 's' puede destruir datos existentes en la base de datos)\e[0m (s/n): "
read first_deploy

if [[ "$first_deploy" == "s" ]]; then
	echo -e "\e[1;33m[INFO] Ejecutando migraciones de Alembic\e[0m"
	docker compose exec api alembic upgrade head
	echo -e "\e[1;32m[SUCCESS] Migraciones de Alembic ejecutadas exitosamente\e[0m"

	echo -e "\e[1;33m[INFO] Cargando datos iniciales de Django\e[0m"
	docker compose exec webapp python manage.py loaddata fixtures/datos_iniciales.json
	echo -e "\e[1;32m[SUCCESS] Datos iniciales cargados\e[0m"
fi
