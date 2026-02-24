#!/bin/bash
# setup-railway.sh - Automatizar configuración inicial de Railway
# Uso: ./scripts/setup-railway.sh [--staging|--production]

set -e

ENV="${1:-production}"
PROJECT_NAME="qaframework"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║   QA-FRAMEWORK Railway Setup Script       ║"
echo "║   Environment: $ENV                       ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar prerequisitos
echo -e "${YELLOW}Verificando prerequisitos...${NC}"

if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI no está instalado${NC}"
    echo "Instalando Railway CLI..."
    npm install -g @railway/cli
fi

if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ OpenSSL no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisitos OK${NC}"
echo ""

# Login si es necesario
echo -e "${YELLOW}Verificando autenticación...${NC}"
if ! railway whoami &> /dev/null; then
    echo "Necesitas hacer login en Railway..."
    railway login
fi
echo -e "${GREEN}✅ Autenticado${NC}"
echo ""

# Crear o seleccionar proyecto
echo -e "${YELLOW}Configurando proyecto...${NC}"
if railway status &> /dev/null; then
    echo -e "${GREEN}✅ Proyecto ya vinculado${NC}"
else
    echo "Creando nuevo proyecto..."
    railway init --name "$PROJECT_NAME-$ENV"
fi
echo ""

# Crear servicios
echo -e "${YELLOW}Creando servicios de base de datos...${NC}"

# PostgreSQL
echo "Creando PostgreSQL..."
if railway status | grep -q "Postgres"; then
    echo -e "${GREEN}✅ PostgreSQL ya existe${NC}"
else
    railway add --plugin postgresql
    echo -e "${GREEN}✅ PostgreSQL creado${NC}"
fi

# Redis
echo "Creando Redis..."
if railway status | grep -q "Redis"; then
    echo -e "${GREEN}✅ Redis ya existe${NC}"
else
    railway add --plugin redis
    echo -e "${GREEN}✅ Redis creado${NC}"
fi
echo ""

# Crear environment si no existe
echo -e "${YELLOW}Configurando environment...${NC}"
if ! railway environment list 2>/dev/null | grep -q "$ENV"; then
    echo "Creando environment: $ENV"
    railway environment create "$ENV"
fi
echo -e "${GREEN}✅ Environment configurado${NC}"
echo ""

# Configurar variables de entorno
echo -e "${YELLOW}Configurando variables de entorno...${NC}"

# Generar secrets
JWT_SECRET=$(openssl rand -hex 32)
echo -e "${GREEN}✅ JWT_SECRET_KEY generado${NC}"

# Variables críticas
echo "Seteando variables..."
railway variables set --environment "$ENV" JWT_SECRET_KEY="$JWT_SECRET"
railway variables set --environment "$ENV" JWT_ALGORITHM="HS256"
railway variables set --environment "$ENV" JWT_EXPIRATION_HOURS="24"

# Referencias a servicios
railway variables set --environment "$ENV" DATABASE_URL='${{Postgres.DATABASE_URL}}'
railway variables set --environment "$ENV" REDIS_URL='${{Redis.REDIS_URL}}'

# Configuración por ambiente
if [ "$ENV" = "production" ]; then
    railway variables set --environment "$ENV" LOG_LEVEL="INFO"
    railway variables set --environment "$ENV" CORS_ORIGINS='["https://qaframework.io","https://www.qaframework.io"]'
else
    railway variables set --environment "$ENV" LOG_LEVEL="DEBUG"
    railway variables set --environment "$ENV" CORS_ORIGINS='["http://localhost:3000","https://staging.qaframework.io"]'
fi

echo -e "${GREEN}✅ Variables configuradas${NC}"
echo ""

# Mostrar resumen
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║           Setup Completado ✅              ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Revisar variables:"
echo "   railway variables"
echo ""
echo "2. Vincular repositorio (si no está vinculado):"
echo "   railway link"
echo ""
echo "3. Hacer primer deploy:"
echo "   railway up --environment $ENV"
echo ""
echo "4. Configurar dominio:"
echo "   railway domain add api.qaframework.io --environment $ENV"
echo ""
echo "5. Ver logs:"
echo "   railway logs --tail"
echo ""
echo "📚 Documentación:"
echo "   docs/deployment/RAILWAY_TEMPLATES.md"
echo "   docs/deployment/DEPLOYMENT.md"
echo ""
