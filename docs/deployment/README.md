# 📚 Deployment Documentation Index

**QA-FRAMEWORK SaaS - Guías de Deployment**

---

## 📄 Documentos Disponibles

### Setup y Configuración

| Documento | Propósito | Tiempo Lectura |
|-----------|-----------|----------------|
| [CLOUD_PROVIDER_COMPARISON.md](./CLOUD_PROVIDER_COMPARISON.md) | Comparativa Railway vs Fly.io vs Render | 10 min |
| [RAILWAY_TEMPLATES.md](./RAILWAY_TEMPLATES.md) | Comandos y templates para Railway CLI | 5 min |
| [SECRETS_MANAGEMENT.md](./SECRETS_MANAGEMENT.md) | Gestión de secrets en producción | 8 min |
| [PRE_DEPLOY_CHECKLIST.md](./PRE_DEPLOY_CHECKLIST.md) | Checklist antes de cada deploy | 5 min |

### Troubleshooting

| Documento | Propósito | Tiempo Lectura |
|-----------|-----------|----------------|
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Soluciones a problemas comunes | 15 min |

### Scripts de Automatización

| Script | Propósito | Uso |
|--------|-----------|-----|
| `scripts/setup-railway.sh` | Configuración inicial Railway | `./scripts/setup-railway.sh --staging` |
| `scripts/pre-deploy-check.sh` | Validación pre-deploy | `./scripts/pre-deploy-check.sh` |

---

## 🚀 Quick Start

### Primer Deploy (5 pasos)

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Ejecutar setup automático
./scripts/setup-railway.sh --staging

# 3. Validar configuración
./scripts/pre-deploy-check.sh

# 4. Deploy
railway up --environment staging

# 5. Verificar
railway logs --tail
```

---

## 📊 Flujo de Deployment

```
┌─────────────────┐
│  Código en main │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │ ← .github/workflows/deploy.yml
│   CI/CD         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pre-deploy Check│ ← scripts/pre-deploy-check.sh
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build Docker    │ ← Dockerfile
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Railway Deploy │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Health Check   │ ← /health endpoint
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Live! 🎉    │
└─────────────────┘
```

---

## 🎯 Por Ambiente

### Development (Local)
```bash
docker-compose up -d
# http://localhost:8000
```

### Staging
```bash
./scripts/setup-railway.sh --staging
railway up --environment staging
# https://staging.qaframework.io
```

### Production
```bash
./scripts/pre-deploy-check.sh
railway up --environment production
# https://api.qaframework.io
```

---

## 🔗 Links Útiles

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Status:** https://status.railway.app/
- **Railway Docs:** https://docs.railway.app/
- **GitHub Repo:** https://github.com/llllJokerllll/QA-FRAMEWORK

---

## 📝 Contribuir

Si encuentras problemas durante el deployment:

1. Revisa [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Busca en Railway Discord
3. Documenta la solución en `.learnings/INCIDENTS.md`
4. Actualiza esta documentación

---

**Última actualización:** 2026-02-24
**Mantenedor:** Alfred (AI Agent)
