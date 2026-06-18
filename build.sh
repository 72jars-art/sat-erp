#!/usr/bin/env bash
# Salir si ocurre un error
set -o errexit

# 1. Instalar las dependencias
pip install -r requirements.txt

# 2. Convertir archivos estáticos a la carpeta de producción
python manage.py collectstatic --no-input

# 3. Aplicar las migraciones a la base de datos de Neon
python manage.py migrate