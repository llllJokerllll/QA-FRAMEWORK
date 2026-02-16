#!/bin/bash

# Script para diagnosticar y corregir problemas de pytest-asyncio
# QA-FRAMEWORK Dashboard

echo "=== Diagnóstico de pytest-asyncio ==="
echo ""

# Verificar versión de Python
echo "Python version:"
python3 --version
echo ""

# Verificar versión de pytest
echo "pytest version:"
pip show pytest | grep Version
echo ""

# Verificar versión de pytest-asyncio
echo "pytest-asyncio version:"
pip show pytest-asyncio | grep Version
echo ""

# Verificar greenlet
echo "greenlet version:"
pip show greenlet | grep Version
echo ""

echo "=== Problema Conocido ==="
echo "pytest-asyncio 0.25.0 tiene problemas de segmentation fault"
echo "con greenlet >= 3.0.0 y Python 3.12"
echo ""

echo "=== Solución 1: Downgrade de greenlet ==="
echo "Ejecutar:"
echo "  pip install greenlet==2.0.2"
echo ""

echo "=== Solución 2: Actualizar a versiones compatibles ==="
echo "Ejecutar:"
echo "  pip install pytest==8.3.4 pytest-asyncio==0.24.0"
echo ""

echo "=== Solución 3: Recrear entorno virtual ==="
echo "Ejecutar:"
echo "  cd backend"
echo "  rm -rf venv"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  pip install pytest==8.3.3 pytest-asyncio==0.24.0 --force-reinstall"
echo ""

echo "=== Verificar solución ==="
echo "Después de aplicar la solución, ejecutar:"
echo "  pytest tests/unit/test_simple.py -v"
echo ""

echo "=== Script de corrección automática ==="
echo "Este script intentará corregir el problema automáticamente..."

# Intentar corrección automática
echo ""
echo "Instalando greenlet 2.0.2..."
pip install greenlet==2.0.2 --quiet

echo ""
echo "Instalando pytest-asyncio 0.24.0..."
pip install pytest-asyncio==0.24.0 --quiet

echo ""
echo "=== Verificando corrección ==="
python3 -c "import pytest; import asyncio; print('pytest y asyncio importados correctamente')"

echo ""
echo "=== Fin del diagnóstico ==="
echo "Si el problema persiste, por favor recrear el entorno virtual."
