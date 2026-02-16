# Guía de Deployment con Docker - QA-FRAMEWORK Dashboard

**Versión:** 1.0.0  
**Fecha:** 2026-02-16  
**Autor:** Alfred

---

## 📋 Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Arquitectura de Contenedores](#arquitectura-de-contenedores)
3. [Desarrollo Local](#desarrollo-local)
4. [Deployment en Producción](#deployment-en-producción)
5. [Configuración de Variables](#configuración-de-variables)
6. [SSL/HTTPS](#sslhttps)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Backup y Restauración](#backup-y-restauración)
9. [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

### Software Necesario

| Software | Versión Mínima | Propósito |
|----------|----------------|-----------|
| Docker | 24.0+ | Contenedores |
| Docker Compose | 2.20+ | Orquestación |
| Git | 2.40+ | Control de versiones |

### Verificar Instalación

```bash
docker --version
docker compose version
git --version
```

### Recursos Recomendados

| Recurso | Desarrollo | Producción |
|---------|------------|------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disco | 10 GB | 50+ GB |

---

## Arquitectura de Contenedores

### Servicios

```
┌─────────────────────────────────────────────────────────────┐
│                    QA-FRAMEWORK Dashboard                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Frontend  │  │   Backend   │  │  PostgreSQL │         │
│  │   (React)   │  │  (FastAPI)  │  │   (DB)      │         │
│  │   :3000     │  │   :8000     │  │   :5432     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Redis    │  │   Celery    │  │   Nginx     │         │
│  │   (Cache)   │  │  (Worker)   │  │ (Proxy)     │         │
│  │   :6379     │  │   :5555     │  │   :80/443   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Puertos

| Servicio | Puerto Interno | Puerto Externo |
|----------|----------------|----------------|
| Frontend | 3000 | 3000 |
| Backend | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| Flower | 5555 | 5555 |
| Nginx | 80/443 | 80/443 |

---

## Desarrollo Local

### 1. Clonar Repositorio

```bash
git clone https://github.com/anomalyco/QA-FRAMEWORK-DASHBOARD.git
cd QA-FRAMEWORK-DASHBOARD
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables
nano .env
```

### 3. Iniciar Servicios

```bash
# Construir y levantar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Ver estado de contenedores
docker compose ps
```

### 4. Verificar Servicios

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# PostgreSQL
docker compose exec postgres pg_isready

# Redis
docker compose exec redis redis-cli ping
```

### 5. Inicializar Base de Datos

```bash
# Ejecutar migraciones
docker compose exec backend alembic upgrade head

# Crear usuario admin
docker compose exec backend python -c "
from services.auth_service import create_user
create_user('admin@example.com', 'adminpassword', 'Admin')
"
```

### 6. Detener Servicios

```bash
# Detener manteniendo datos
docker compose down

# Detener eliminando volúmenes (⚠️ borra datos)
docker compose down -v
```

---

## Deployment en Producción

### 1. Preparar Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin

# Instalar herramientas útiles
sudo apt install nginx certbot python3-certbot-nginx -y
```

### 2. Configurar Firewall

```bash
# Permitir puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. Crear docker-compose.prod.yml

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - VITE_API_URL=https://api.tudominio.com
    networks:
      - qa-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql+asyncpg://qa_user:${DB_PASSWORD}@postgres:5432/qa_framework_db
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_HOST=redis
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    networks:
      - qa-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=qa_framework_db
      - POSTGRES_USER=qa_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - qa-network
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - qa-network
    restart: always

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A core.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://qa_user:${DB_PASSWORD}@postgres:5432/qa_framework_db
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_HOST=redis
    depends_on:
      - redis
      - postgres
    networks:
      - qa-network
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_files:/var/www/static
    depends_on:
      - frontend
      - backend
    networks:
      - qa-network
    restart: always

volumes:
  postgres_data:
  redis_data:
  static_files:

networks:
  qa-network:
    driver: bridge
```

### 4. Configurar Variables de Producción

```bash
# Crear .env.prod
cat > .env.prod << EOF
# Database
POSTGRES_DB=qa_framework_db
POSTGRES_USER=qa_user
DB_PASSWORD=<generar-password-seguro>

# Security
SECRET_KEY=<generar-secret-key-largo>

# API
VITE_API_URL=https://api.tudominio.com

# External Services (opcional)
JIRA_URL=https://tuempresa.atlassian.net
JIRA_API_TOKEN=<token>
EOF

# Generar secretos seguros
openssl rand -hex 32  # Para SECRET_KEY
openssl rand -base64 24  # Para DB_PASSWORD
```

### 5. Desplegar

```bash
# Construir imágenes
docker compose -f docker-compose.prod.yml build

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# Verificar
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### 6. Configurar SSL con Let's Encrypt

```bash
# Obtener certificado
sudo certbot --nginx -d tudominio.com -d api.tudominio.com

# Auto-renovación
sudo certbot renew --dry-run
```

---

## Configuración de Variables

### Variables Obligatorias

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Clave secreta para JWT | String aleatorio de 64+ caracteres |
| `VITE_API_URL` | URL del backend | `https://api.tudominio.com` |

### Variables Opcionales

| Variable | Default | Descripción |
|----------|---------|-------------|
| `REDIS_HOST` | localhost | Host de Redis |
| `REDIS_PORT` | 6379 | Puerto de Redis |
| `CORS_ORIGINS` | * | Orígenes permitidos |
| `LOG_LEVEL` | INFO | Nivel de logging |

### Variables de Integración

| Variable | Descripción |
|----------|-------------|
| `JIRA_URL` | URL de instancia Jira |
| `JIRA_API_TOKEN` | Token de API de Jira |
| `ZEPHYR_API_KEY` | API Key de Zephyr |
| `AZURE_DEVOPS_TOKEN` | Token de Azure DevOps |

---

## SSL/HTTPS

### Configuración de Nginx

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    # Upstreams
    upstream frontend {
        server frontend:3000;
    }
    
    upstream backend {
        server backend:8000;
    }
    
    # HTTP -> HTTPS redirect
    server {
        listen 80;
        server_name tudominio.com api.tudominio.com;
        return 301 https://$server_name$request_uri;
    }
    
    # HTTPS - Frontend
    server {
        listen 443 ssl http2;
        server_name tudominio.com;
        
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    
    # HTTPS - Backend API
    server {
        listen 443 ssl http2;
        server_name api.tudominio.com;
        
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        
        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket support
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

---

## Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f backend

# Últimas 100 líneas
docker compose logs --tail=100 backend
```

### Estructura de Logs

```python
# Los logs se almacenan en:
/var/log/qa-framework/
├── backend/
│   ├── access.log
│   ├── error.log
│   └── application.log
├── celery/
│   └── worker.log
└── nginx/
    ├── access.log
    └── error.log
```

### Métricas con Prometheus (Opcional)

```yaml
# Añadir a docker-compose.prod.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
```

---

## Backup y Restauración

### Backup de Base de Datos

```bash
# Backup manual
docker compose exec postgres pg_dump -U qa_user qa_framework_db > backup_$(date +%Y%m%d).sql

# Backup automático (cron)
echo "0 2 * * * docker compose exec -T postgres pg_dump -U qa_user qa_framework_db > /backups/backup_\$(date +\%Y\%m\%d).sql" | crontab -
```

### Restaurar Base de Datos

```bash
# Restaurar desde backup
cat backup_20260216.sql | docker compose exec -T postgres psql -U qa_user qa_framework_db
```

### Backup de Volúmenes

```bash
# Crear backup de todos los volúmenes
docker run --rm -v qa-framework_postgres_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_$(date +%Y%m%d).tar.gz /data
```

---

## Troubleshooting

### Problemas Comunes

#### 1. Error: "Connection refused"

```bash
# Verificar que el servicio está corriendo
docker compose ps

# Verificar logs
docker compose logs backend

# Reiniciar servicio
docker compose restart backend
```

#### 2. Error: "Database connection failed"

```bash
# Verificar PostgreSQL
docker compose exec postgres pg_isready

# Verificar credenciales en .env
cat .env | grep DATABASE

# Reiniciar PostgreSQL
docker compose restart postgres
```

#### 3. Error: "Permission denied"

```bash
# Corregir permisos
sudo chown -R $USER:$USER .

# O usar sudo para docker
sudo docker compose up -d
```

#### 4. Contenedor no inicia

```bash
# Ver logs detallados
docker compose logs --tail=100 <servicio>

# Reconstruir imagen
docker compose build --no-cache <servicio>
docker compose up -d <servicio>
```

#### 5. Out of memory

```bash
# Ver uso de recursos
docker stats

# Limitar memoria en docker-compose
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Comandos Útiles

```bash
# Ver estado de todos los contenedores
docker compose ps

# Reiniciar todos los servicios
docker compose restart

# Ver uso de disco
docker system df

# Limpiar recursos no usados
docker system prune -a

# Entrar a contenedor
docker compose exec backend bash

# Ejecutar comando en contenedor
docker compose exec backend python -c "print('test')"
```

---

## Checklist de Deployment

### Pre-Deployment

- [ ] Variables de entorno configuradas en `.env.prod`
- [ ] Secretos generados con `openssl rand`
- [ ] SSL certificados obtenidos
- [ ] Firewall configurado
- [ ] Backup plan definido

### Deployment

- [ ] Imágenes construidas correctamente
- [ ] Contenedores iniciados sin errores
- [ ] Migraciones de BD ejecutadas
- [ ] Usuario admin creado
- [ ] Health checks pasando

### Post-Deployment

- [ ] Login funciona correctamente
- [ ] API responde en `/docs`
- [ ] SSL configurado y funcionando
- [ ] Logs sin errores críticos
- [ ] Monitoreo activo (si aplica)
- [ ] Backup automático configurado

---

## Soporte

Para problemas o preguntas:

1. Revisar logs: `docker compose logs -f`
2. Consultar documentación: `/docs`
3. Crear issue en GitHub
4. Contactar: support@tudominio.com

---

**Última actualización:** 2026-02-16  
**Mantenido por:** Alfred - DevOps Team
