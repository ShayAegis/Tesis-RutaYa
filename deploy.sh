#!/bin/bash

set -e 

echo -e "\e[1;33m[INFO] Levantando contenedores de Docker\e[0m"
docker compose up -d
echo -e "\e[1;32m[SUCCESS] Contenedores levantados exitosamente\e[0m"

echo -e "\e[1;33m[INFO] Ejecutando migraciones de Django\e[0m"
docker compose exec webapp python3 manage.py makemigrations && \
docker compose exec webapp python3 manage.py migrate
echo -e "\e[1;32m[SUCCESS] Migraciones ejecutadas exitosamente\e[0m"

echo -e "Desea cargar los datos iniciales a la base de datos? \e[1;31m(Esto sobreescribirá datos existentes en la base de datos)\e[0m (s/n): "
read load_defaults

if [[ "$load_defaults" == "s" ]]; then
	docker compose exec webapp python manage.py loaddata fixtures/datos_iniciales.json
	echo -e "\e[1;32m[SUCCESS] Datos iniciales cargados\e[0m"
fi
