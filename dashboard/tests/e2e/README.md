# Tests E2E - QA-FRAMEWORK Dashboard

Tests end-to-end usando **Playwright con Python**.

## Requisitos

- Python 3.11+
- Playwright con Chromium
- Backend y Frontend corriendo

## Instalación

```bash
cd backend
source venv/bin/activate
pip install pytest-playwright
playwright install chromium
```

## Ejecutar Tests

### Todos los tests E2E
```bash
pytest tests/e2e/ -v -m e2e
```

### Tests específicos
```bash
# Solo login
pytest tests/e2e/test_login.py -v

# Solo suites
pytest tests/e2e/test_suites.py -v

# Solo casos
pytest tests/e2e/test_cases.py -v

# Solo ejecuciones
pytest tests/e2e/test_executions.py -v
```

### Con headed mode (ver navegador)
```bash
HEADLESS=false pytest tests/e2e/ -v
```

### Con screenshots en fallo
```bash
pytest tests/e2e/ -v --screenshot on-failure
```

## Estructura

```
tests/e2e/
├── conftest.py          # Fixtures compartidas
├── test_login.py        # Tests de autenticación
├── test_suites.py       # Tests CRUD de suites
├── test_cases.py        # Tests CRUD de casos
├── test_executions.py   # Tests de ejecuciones
├── screenshots/         # Screenshots de fallos
└── pytest.ini          # Configuración de pytest
```

## Cobertura

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| Login | 8 | Autenticación, logout, validación |
| Suites | 10 | CRUD completo, navegación |
| Cases | 12 | CRUD, filtrado, priorización |
| Executions | 15 | Creación, monitoreo, reportes |

**Total: 45+ tests E2E**

## CI/CD

Para ejecutar en CI:

```bash
# Instalar dependencias
pip install -r backend/requirements.txt
playwright install chromium --with-deps

# Ejecutar tests
pytest tests/e2e/ -v --headless --report=html
```

## Configuración

Variables de entorno:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `BASE_URL` | http://localhost:3000 | URL del frontend |
| `API_URL` | http://localhost:8000 | URL del backend |
| `HEADLESS` | true | Ejecutar sin UI |

## Fixtures Disponibles

| Fixture | Descripción |
|---------|-------------|
| `browser` | Browser compartido (session) |
| `context` | Contexto aislado por test |
| `page` | Página nueva por test |
| `authenticated_page` | Página con usuario logueado |
| `helpers` | Utilidades de test |

## Troubleshooting

### Error: "playwright not found"
```bash
playwright install chromium
```

### Error: "Timeout waiting for selector"
- Verificar que el frontend está corriendo
- Aumentar timeout en el test
- Revisar selectores CSS

### Error: "Connection refused"
- Verificar que backend corre en puerto 8000
- Verificar que frontend corre en puerto 3000
