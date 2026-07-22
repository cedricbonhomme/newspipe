# Experimento de modernización (Strangler Fig): Flask → FastAPI

Este documento explica cómo levantar el experimento de la entrega final desde cero, en
cualquier máquina del equipo. La fachada FastAPI (`asgi.py`) sirve de forma nativa los dos
requisitos migrados y delega todo lo demás al Flask legado, sobre la misma base de datos
PostgreSQL.

**Requisitos migrados**

- R1. Gestión de feeds: `GET /api/v2.0/feeds` y `POST /api/v2.0/feed` (`newspipe/api_v3/feeds.py`)
- R2. Gestión de artículos: `GET /api/v2.0/articles` (con filtros) y `GET /api/v2.0/article/{id}` (`newspipe/api_v3/articles.py`)

**Usuarios de prueba** (los crea `seed_experiment.py`): `admin/admin123` (admin) y `apiuser/api123` (rol API).

## 0. Prerrequisitos

- Python 3.10 o superior (probado con 3.13)
- Docker Desktop corriendo (para el contenedor de PostgreSQL)
- Estar en el branch del experimento: `git fetch && git checkout experimento`

Los comandos siguientes están en dos sabores: **PowerShell** (Windows) y **bash** (Git Bash, Linux o Mac). En Linux y Mac la ruta del venv es `.venv/bin/python` en lugar de `.venv/Scripts/python`.

## 1. Preparar el entorno (una sola vez)

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e . fastapi uvicorn a2wsgi httpx
```

## 2. Levantar la base de datos (PostgreSQL en Docker)

```powershell
docker compose -f docker-compose-experiment.yml up -d
```

## 3. Crear el esquema y sembrar usuarios y datos (una sola vez)

PowerShell:

```powershell
$env:NEWSPIPE_CONFIG = "experiment-postgresql.py"
$env:FLASK_APP = "app.py"
.venv\Scripts\python -m flask db_init
.venv\Scripts\python seed_experiment.py
```

bash:

```bash
export NEWSPIPE_CONFIG=experiment-postgresql.py FLASK_APP=app.py
.venv/Scripts/python -m flask db_init
.venv/Scripts/python seed_experiment.py
```

`seed_experiment.py` es idempotente: crea los usuarios `admin` y `apiuser`, 2 feeds y 4
artículos si no existen. El mensaje `fatal: No names found...` que imprimen los comandos
`flask` es un `git describe` interno del proyecto y se puede ignorar.

## 4. Correr las dos versiones (dos terminales)

Terminal 1, el legado puro (Flask, puerto 5000, la línea base):

```powershell
$env:NEWSPIPE_CONFIG = "experiment-postgresql.py"; $env:FLASK_APP = "app.py"
.venv\Scripts\python -m flask run --port 5000 --debug --no-reload
```

Terminal 2, la fachada modernizada (FastAPI con el legado adentro, puerto 8000):

```powershell
$env:NEWSPIPE_CONFIG = "experiment-postgresql.py"
.venv\Scripts\python -m uvicorn asgi:app --port 8000
```

El `--debug` del legado es necesario: sin él, Flask-Talisman fuerza una redirección a HTTPS
y las peticiones locales fallan.

## 5. Verificar la paridad funcional

```powershell
.venv\Scripts\python parity_check.py
```

El script compara el legado (5000) contra la fachada (8000): paridad de payload de R1 y R2,
creación por ambas rutas sobre la misma base, scoping por usuario, convivencia de rutas no
migradas y contrato OpenAPI. **Resultado esperado: 16/16 verificaciones exitosas.** Es
idempotente, se puede correr las veces que haga falta.

## 6. Grabar el video de demostración

El guion escena por escena, con los comandos exactos para pegar y la narración sugerida,
está en `docs/semana-8/guion-video-demostracion.md` de este mismo repositorio.

Los puntos clave que el video debe mostrar:

- `GET /api/v2.0/feeds` en 5000 (legado) y en 8000 (fachada): misma respuesta sobre la misma base.
  Ojo: el legado exige un body JSON (`curl -X GET -d '{"limit": 10}' -H "Content-Type: application/json"`)
  o query args; la fachada acepta query params normales.
- `POST /api/v2.0/feed` en 8000 con solo `{"title": ..., "link": ...}`: la fachada aplica los
  defaults declarados en el esquema. El mismo POST en el legado exige todos los campos de la
  whitelist. El feed creado por una ruta es visible de inmediato por la otra.
- `http://localhost:8000/docs`: contrato OpenAPI generado automáticamente (no existe en el legado).
- Convivencia: `http://localhost:8000/login` es la web legada servida a través de la fachada,
  y `GET /api/v2.0/feed/1` (no migrado) también se delega al legado.
- La corrida de `parity_check.py` terminando en 16/16.
