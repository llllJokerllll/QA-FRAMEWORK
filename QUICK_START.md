# Quick Start Guide - QA-FRAMEWORK

**Fecha:** 2026-03-10
**Objetivo:** Ayudar a nuevos usuarios a probar QA-FRAMEWORK en <10 minutos

---

## 🚀 Introducción Rápida

QA-FRAMEWORK es un framework moderno de automatización de pruebas con:
- ✅ **AI-Powered Testing** - Generación y auto-reparación de tests
- ✅ **Self-Healing** - Tests que se auto-reparan cuando fallan
- ✅ **Multi-Tenant** - Aislamiento completo por organización
- ✅ **Cloud-Ready** - Deploy fácil en Railway, Vercel, AWS
- ✅ **Analytics** - Reportes detallados con historial

---

## 📋 Prerrequisitos

Para usar QA-FRAMEWORK necesitas:

1. **Cuenta en Railway** (backend hosting)
   - Registrarte en railway.app
   - Crear proyecto "qa-framework-backend"

2. **Cuenta en Vercel** (frontend hosting)
   - Registrarte en vercel.com
   - Importar el frontend

3. **Stripe Account** (opcional - para pagar)
   - Registrarte en stripe.com
   - Configurar payment methods

4. **Repositorio Git** (para deploy automático)
   - GitHub, GitLab o Bitbucket

---

## 🏗️ Arquitectura Resumida

```
┌─────────────────┐
│  Frontend React │ ← Usuario interacts
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Backend FastAPI│ ← Lógica y API
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │PostgreSQL│  │  Redis  │  │ Playwright│
    │  (DB)   │  │ (Cache) │  │ (Browser)│
    └─────────┘  └─────────┘  └─────────┘
```

---

## 📥 Setup en 5 Minutos

### Paso 1: Clonar Repositorio

```bash
git clone https://github.com/your-username/qa-framework.git
cd qa-framework
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus datos
nano .env
```

Variables de entorno requeridas:
```bash
# Database
DATABASE_URL=postgresql://user:password@railway.app:port/db

# Redis
REDIS_URL=redis://railway.app:port

# Stripe
STRIPE_API_KEY=sk_live_xxx

# OpenRouter (para AI)
OPENROUTER_API_KEY=sk-or-v1-xxx
```

### Paso 3: Desplegar Backend en Railway

```bash
# Con Railway CLI
railway login
railway init
railway up

# O con GitHub Actions
# El deploy se hace automáticamente cuando pusas al repositorio
```

**Verificar:** https://qa-framework-backend.railway.app/health

### Paso 4: Desplegar Frontend en Vercel

```bash
# Con Vercel CLI
npx vercel

# O con GitHub
# Vercel detectará el repo automáticamente
```

**Verificar:** https://tu-proyecto.vercel.app

---

## 🎯 Primer Test Run

### Opción A: Usar UI Web

1. Abre https://frontend-phi-three-52.vercel.app
2. Click en "Login"
3. Regístrate con email (o GitHub OAuth)
4. Crear nuevo proyecto
5. Escribe un test case
6. Click en "Run Tests"

### Opción B: Usar API

```bash
# Crear test run
curl -X POST https://qa-framework-backend.railway.app/api/v1/test-runs \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "test-001",
    "name": "Login Flow Test",
    "metadata": {
      "browser": "chrome",
      "environment": "staging"
    }
  }'

# Obtener resultados
curl https://qa-framework-backend.railway.app/api/v1/test-runs/{test_id}/results
```

### Opción C: Usar Playwright (Automatizado)

```bash
cd QA-FRAMEWORK/dashboard
npm install

# Crear test
npx playwright test --headed
```

---

## 🎨 Características Principales

### 1. Self-Healing Tests

Si un elemento cambia (CSS, ID, texto), el test se auto-repara:

```python
# Test que falla por selector
def test_login():
    assert page.locator("#username").fill("joker@example.com")
    assert page.locator("#password").fill("password123")
    assert page.locator("button[type='submit']").click()

# Después de un cambio en el CSS
# El test se auto-repara con AI detection
```

### 2. AI Test Generation

Genera tests desde requirements:

```python
# Input: User story
user_story = """
Given I'm on the login page
When I enter valid credentials
Then I should be redirected to dashboard
"""

# Output: Test generado automáticamente
test_login_flow()
```

### 3. Multi-Tenant Architecture

Cada organización tiene:
- Aislamiento completo de datos
- Configuration separada
- Limits personalizados

```python
# Tenant context is automatically set
def test_run():
    # Tests execution is tenant-aware
    assert test_run.status == "passed"
```

### 4. Comprehensive Reporting

HTML reports con:
- Test execution history
- Pass/fail rates
- Performance metrics
- Screenshots on failure

```bash
# Generar reporte HTML
curl https://qa-framework-backend.railway.app/api/v1/test-runs/{id}/report?format=html \
  --output report.html

# Abrir en navegador
open report.html
```

---

## 🔧 Configuración Básica

### Crear Proyecto

```bash
# Con API
curl -X POST https://qa-framework-backend.railway.app/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E-commerce Tests",
    "description": "Tests para página de productos"
  }'
```

### Crear Test Run

```bash
curl -X POST https://qa-framework-backend.railway.app/api/v1/test-runs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project-001",
    "test_id": "test-e-commerce-001",
    "name": "E-commerce Checkout Flow",
    "status": "running",
    "metadata": {
      "browser": "chrome",
      "viewport": "1920x1080",
      "environment": "staging"
    }
  }'
```

### Obtener Resultados

```bash
# Obtener test runs
curl https://qa-framework-backend.railway.app/api/v1/test-runs \
  -H "Authorization: Bearer YOUR_TOKEN"

# Obtener resultados de un test
curl https://qa-framework-backend.railway.app/api/v1/test-runs/{id}/results \
  -H "Authorization: Bearer YOUR_TOKEN"

# Obtener métricas
curl https://qa-framework-backend.railway.app/api/v1/test-runs/{id}/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Dashboard de Monitoring

QA-FRAMEWORK tiene dashboards de monitoring automáticos:

### Business Metrics (Dashboard de Negocio)
URL: http://localhost:3000/d/qa-framework-business (cuando estés corriendo local)

Métricas:
- Active Test Runs
- Test Success Rate
- Error Rate
- P95 Latency
- Requests Last Hour
- Active Users

### API Performance
URL: http://localhost:3000/d/api-performance

Métricas:
- Request duration percentiles
- Error rate by endpoint
- Request rate

### Database Metrics
URL: http://localhost:3000/d/database-metrics

Métricas:
- Connection pool usage
- Cache hit ratio
- Transaction throughput

### Cache Performance (Redis)
URL: http://localhost:3000/d/cache-performance

Métricas:
- Memory usage
- Hit/miss ratio
- Operations per second

---

## 🛠️ Comandos CLI Útiles

### Instalar QA-FRAMEWORK

```bash
# Via pip
pip install qa-framework

# Via docker
docker pull qaframework/qa-framework:latest
docker run -p 8000:8000 qaframework/qa-framework:latest

# Via npm (Frontend)
npm install -g qa-framework-cli
qa-framework init
```

### Ejecutar Tests

```bash
# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Todos los tests
pytest tests/ -v --html=report.html
```

### Generar Reportes

```bash
# HTML report
pytest tests/ --html=report.html --self-contained-html

# JSON report
pytest tests/ --json-report --json-report-file=report.json

# Allure report
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

---

## 🐛 Troubleshooting

### Backend no responde

```bash
# Verificar health check
curl https://qa-framework-backend.railway.app/health

# Ver logs de Railway
railway logs --follow

# Verificar variables de entorno
railway variables
```

### Database connection error

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión manual
psql $DATABASE_URL -c "SELECT version();"

# Verificar Railway logs
railway logs
```

### Redis connection error

```bash
# Verificar REDIS_URL
echo $REDIS_URL

# Probar conexión manual
redis-cli -h <host> -p <port> ping

# Verificar Railway logs
railway logs
```

### Frontend no carga

```bash
# Verificar Vercel deploy
npx vercel ls

# Verificar logs
npx vercel logs

# Limpiar cache y redeploy
npx vercel --prod --force
```

---

## 📚 Recursos Adicionales

- **Documentación Completa:** https://docs.qaframework.io
- **API Reference:** https://docs.qaframework.io/api
- **GitHub Repo:** https://github.com/your-username/qa-framework
- **Discord Community:** https://discord.gg/qaframework

---

## ❓ FAQ

**Q: ¿Puedo usar QA-FRAMEWORK sin pagar?**
A: Sí, versión gratuita con 3 proyectos y 100 test runs/mes.

**Q: ¿Qué browsers soporta?**
A: Chrome, Firefox, Safari, Edge (Playwright). Para IE11 usa Selenium.

**Q: ¿Puedo ejecutar tests en paralelo?**
A: Sí, con pytest-xdist: `pytest tests/ -n auto`

**Q: ¿Cómo backup mis tests?**
A: Los tests están en el repositorio Git. Puedes usar GitHub Actions para automatización.

**Q: ¿Soporta CI/CD integrations?**
A: Sí, GitHub Actions, GitLab CI, CircleCI, Jenkins.

**Q: ¿Puedo integrar con Jira?**
A: Sí, webhook de resultados a Jira disponible.

---

## ✨ Next Steps

1. **Explorar Dashboard**
   - Crear tu primer proyecto
   - Ejecutar un test
   - Ver resultados

2. **Leer Documentación**
   - API Reference
   - Customization Guide
   - Best Practices

3. **Conectar a CI/CD**
   - GitHub Actions
   - Automatizar tests en cada PR

4. **Invitar Equipo**
   - Invitar usuarios al dashboard
   - Configurar roles y permissions

---

**¿Listo para empezar?**

👉 [Ir a QA-FRAMEWORK Dashboard](https://frontend-phi-three-52.vercel.app)

**¿Necesitas ayuda?**
- 📧 Email: support@qaframework.io
- 💬 Discord: https://discord.gg/qaframework
- 📚 Docs: https://docs.qaframework.io

---

*Quick Start Guide v1.0*
*Fecha: 2026-03-10*
*Autor: Alfred (CEO Agent)*
