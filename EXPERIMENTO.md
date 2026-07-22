# Experimento de modernización (Strangler Fig): Flask → FastAPI

Este documento explica cómo correr el experimento de la entrega final: la fachada
FastAPI (`asgi.py`) sirve de forma nativa los dos requisitos migrados y delega todo
lo demás al Flask legado, sobre la misma base de datos PostgreSQL.

**Requisitos migrados**

- R1. Gestión de feeds: `GET /api/v2.0/feeds` y `POST /api/v2.0/feed` (`newspipe/api_v3/feeds.py`)
- R2. Gestión de artículos: `GET /api/v2.0/articles` (con filtros) y `GET /api/v2.0/article/{id}` (`newspipe/api_v3/articles.py`)

## 1. Preparar el entorno

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e . fastapi uvicorn a2wsgi httpx
```

## 2. Levantar la base de datos (PostgreSQL en Docker)

```bash
docker compose -f docker-compose-experiment.yml up -d
```

## 3. Inicializar y sembrar datos

```bash
export NEWSPIPE_CONFIG=experiment-postgresql.py
export FLASK_APP=app.py
.venv/Scripts/python -m flask db_init
.venv/Scripts/python -m flask create_admin --nickname admin --password admin123
.venv/Scripts/python seed_experiment.py
```

## 4. Correr las dos versiones

Terminal 1, el legado puro (Flask, puerto 5000):

```bash
NEWSPIPE_CONFIG=experiment-postgresql.py FLASK_APP=app.py \
  .venv/Scripts/python -m flask run --port 5000 --debug --no-reload
```

Terminal 2, la fachada modernizada (FastAPI + legado adentro, puerto 8000):

```bash
NEWSPIPE_CONFIG=experiment-postgresql.py \
  .venv/Scripts/python -m uvicorn asgi:app --port 8000
```

## 5. Verificar la paridad funcional

```bash
.venv/Scripts/python parity_check.py
```

El script compara el legado (5000) contra la fachada (8000): paridad de payload de
R1 y R2, creación por ambas rutas sobre la misma base, scoping por usuario,
convivencia de rutas no migradas y contrato OpenAPI. Resultado esperado: 16/16.

## 6. Puntos para el video de demostración

- `GET /api/v2.0/feeds` en 5000 (legado) y en 8000 (fachada): misma respuesta.
  Ojo: el legado exige un body JSON (`curl -X GET -d '{"limit": 10}' -H "Content-Type: application/json"`)
  o query args; la fachada acepta query params normales.
- `POST /api/v2.0/feed` en 8000 con solo `{"title": ..., "link": ...}`: la fachada
  aplica defaults declarados. El mismo POST en el legado exige todos los campos de
  la whitelist.
- `http://localhost:8000/docs`: contrato OpenAPI generado (no existe en el legado).
- Convivencia: `http://localhost:8000/login` es la web legada servida a través de
  la fachada; `GET /api/v2.0/feed/1` (no migrado) también se delega al legado.

Usuarios de prueba: `admin/admin123` (admin) y `apiuser/api123` (rol API).
