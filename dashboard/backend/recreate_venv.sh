#!/bin/bash
# Script para recrear el entorno virtual del backend
# Resuelve el problema de pytest-asyncio segmentation fault

set -e

# Cambiar al directorio del backend
cd /home/ubuntu/.openclaw/workspace/QA-FRAMEWORK-DASHBOARD/backend

echo "🗑️  Eliminando venv anterior..."
rm -rf venv

echo "📦 Creando nuevo venv..."
python3 -m venv venv

echo "🔄 Activando venv..."
source venv/bin/activate

echo "⬆️  Actualizando pip..."
pip install --upgrade pip setuptools wheel

echo "📚 Instalando dependencias..."
pip install -r requirements.txt

echo "🧪 Instalando herramientas de testing específicas..."
pip install pytest==8.3.3 pytest-asyncio==0.24.0 --force-reinstall

echo "✅ Verificando instalación..."
python3 -c "import pytest; print(f'pytest {pytest.__version__} OK')"
python3 -c "import pytest_asyncio; print(f'pytest-asyncio {pytest_asyncio.__version__} OK')"

echo ""
echo "🎉 Entorno virtual recreado exitosamente!"
echo "Para activar: source venv/bin/activate"
