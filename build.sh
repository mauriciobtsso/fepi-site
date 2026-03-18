#!/usr/bin/env bash
# Saia do script caso ocorra algum erro
set -o errexit

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Garantindo que a pasta staticfiles existe..."
mkdir -p staticfiles

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "Aplicando migrações no banco de dados..."
python manage.py migrate