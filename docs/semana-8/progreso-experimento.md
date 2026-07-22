# Progreso del experimento de modernización (semana 8)

> Estado al 21 de julio de 2026. Documento interno del equipo para continuar el trabajo.
> **El experimento ya está ejecutado y verificado: 16/16 comprobaciones de paridad exitosas sobre PostgreSQL.**
> Lo que queda pendiente está en la sección 6 de este documento.

## 1. Qué se hizo

Se ejecutó el experimento del pre-experimento planeado: una fachada FastAPI (patrón Strangler Fig) que sirve de forma nativa los dos requisitos migrados y delega todo lo demás al Flask legado, ambos sobre la misma base de datos PostgreSQL.

- **R1. Gestión de feeds:** `GET /api/v2.0/feeds` y `POST /api/v2.0/feed` en FastAPI con esquemas Pydantic.
- **R2. Gestión de artículos:** `GET /api/v2.0/articles` (con filtros `feed_id`, `readed`, `limit`) y `GET /api/v2.0/article/{id}` en FastAPI.
- **Convivencia (transversal):** la interfaz web y el resto de la API v2 se delegan al legado sin cambios a través del `WSGIMiddleware` de `a2wsgi`.

Los routers migrados se publican bajo el **mismo prefijo `/api/v2.0` del legado**: los consumidores conservan sus URL y no se enteran de la migración. Los routers reutilizan los `FeedController`/`ArticleController` y los modelos SQLAlchemy existentes, por eso la paridad sobre la misma base de datos es automática.

## 2. Archivos del experimento en el repo

**Ya están commiteados y publicados en el branch `experimento`** del repo del equipo (commit `1819606`, "First POC commit", 11 archivos): https://github.com/ModernizacionGrupo9/newspipe/tree/experimento. Para trabajar sobre ellos: `git fetch && git checkout experimento`.

| Archivo | Qué es |
| :--- | :--- |
| `newspipe/api_v3/__init__.py` | Paquete del incremento FastAPI (documentación del propósito) |
| `newspipe/api_v3/schemas.py` | Esquemas Pydantic: `FeedIn`, `FeedOut`, `ArticleOut` (el contrato declarado que reemplaza el parseo manual de `common.py`) |
| `newspipe/api_v3/deps.py` | Autenticación HTTP Basic como dependencia (`get_current_user`, `require_api_right`), misma semántica del decorador `authenticate` del legado |
| `newspipe/api_v3/feeds.py` | Router de R1 (listado y creación de feeds) |
| `newspipe/api_v3/articles.py` | Router de R2 (listado con filtros y consulta por id) |
| `asgi.py` | Shell de la fachada Strangler Fig (FastAPI + mount del Flask legado) |
| `docker-compose-experiment.yml` | PostgreSQL 16 en contenedor (la base compartida) |
| `instance/experiment-postgresql.py` | Configuración de Newspipe apuntando al PostgreSQL del compose |
| `seed_experiment.py` | Semilla reproducible: 2 feeds y 4 artículos para el usuario admin |
| `parity_check.py` | Las 16 verificaciones automatizadas legado vs fachada (idempotente, se puede correr N veces) |
| `EXPERIMENTO.md` | Runbook completo: cómo montar todo desde cero + guion sugerido del video de demostración |

La evidencia de la corrida quedó en `docs/semana-8/entregable/resultados/paridad-postgresql.txt`.

**Nota:** el `.venv/` local y la base `instance/newspipe.db` (de la corrida SQLite inicial) quedaron correctamente por fuera del commit y NO se deben commitear.

## 3. Cómo reproducirlo (resumen, el detalle está en EXPERIMENTO.md)

```bash
# 1. Entorno (una sola vez)
python -m venv .venv
.venv/Scripts/python -m pip install -e . fastapi uvicorn a2wsgi httpx

# 2. Base de datos
docker compose -f docker-compose-experiment.yml up -d

# 3. Esquema, usuarios y datos (una sola vez)
export NEWSPIPE_CONFIG=experiment-postgresql.py FLASK_APP=app.py
.venv/Scripts/python -m flask db_init
.venv/Scripts/python seed_experiment.py   # crea admin, apiuser, 2 feeds y 4 articulos

# 4. Los dos servidores (terminales separadas)
.venv/Scripts/python -m flask run --port 5000 --debug --no-reload   # legado puro
.venv/Scripts/python -m uvicorn asgi:app --port 8000                # fachada modernizada

# 5. Verificación
.venv/Scripts/python parity_check.py    # esperado: 16/16
```

Usuarios de prueba: `admin/admin123` (admin) y `apiuser/api123` (rol API, sin admin). Ambos los crea `seed_experiment.py` automáticamente (`parity_check.py` necesita los dos). El contrato OpenAPI generado se ve en `http://localhost:8000/docs`.

## 4. Resultados

Las 16 verificaciones de `parity_check.py` pasaron sobre PostgreSQL (y antes, la misma batería sobre SQLite):

1. R1 `GET /feeds`: mismo status y paridad de payload campo a campo entre legado y fachada.
2. R1 scoping por usuario: `apiuser` ve exactamente lo mismo por ambas rutas y nunca los feeds del admin.
3. R1 `POST /feed` responde 201 por ambas rutas y **lo creado por una ruta es visible de inmediato por la otra** (misma base, sin sincronización).
4. R2 `GET /articles` (sin filtro, con `feed_id`, con `readed`): paridad completa.
5. R2 `GET /article/1` paridad, y `GET /article/9999` responde 404 en la fachada.
6. Convivencia: `GET /feed/1` (no migrado) y la web `/login` atraviesan la fachada y los atiende el legado.
7. OpenAPI generado con los 4 endpoints migrados.

## 5. Hallazgos técnicos (leer antes de continuar la migración)

1. **Contexto de aplicación Flask por hilo.** La capa de datos del legado (Flask-SQLAlchemy) necesita un `application.app_context()` activo, y el contexto es **local al hilo**. FastAPI puede ejecutar las dependencias y el cuerpo del endpoint en hilos distintos, así que NO sirve abrir un contexto "por petición" en una dependencia: **cada dependencia y cada endpoint abren su propio contexto** (ver `deps.py` y los routers). Si agregan endpoints nuevos, sigan ese patrón.
2. **La convivencia es por método HTTP, no solo por ruta.** Un `PUT /api/v2.0/article/1` (no migrado) atraviesa la fachada y lo atiende el legado, aunque el `GET` de esa misma ruta esté migrado. Starlette prefiere la coincidencia completa del mount del legado sobre la coincidencia parcial (ruta sí, método no) del router. O sea: se puede migrar operación por operación, no hace falta migrar la ruta completa.
3. **El contrato informal del legado.** El `GET` de colecciones del legado exige un body JSON (`curl -X GET -d '{"limit": 10}' -H "Content-Type: application/json"`) o query args, y da errores crípticos sin el `Content-Type`. El `POST /feed` legado exige TODOS los campos de la whitelist en el body (si falta uno, falla). La fachada solo pide `title` y `link`. Esto es evidencia directa del problema de mantenibilidad y vale la pena mostrarlo en el video.
4. **Talisman fuerza HTTPS fuera del modo debug.** Por eso el legado se corre con `--debug`. Bajo Uvicorn la fachada respeta el `DEBUG=True` de la config. En un despliegue real habría que terminar TLS o ajustar la política.
5. **Ruido inofensivo:** los comandos `flask` imprimen `fatal: No names found, cannot describe anything.` (un `git describe` interno del proyecto). Se puede ignorar.

## 6. Qué falta (para repartir entre el equipo)

| Pendiente | Detalle | Dónde |
| :--- | :--- | :--- |
| Respuesta Apigee | La sección 1.4 del entregable es un BORRADOR con conocimiento general de Apigee. Hay que validarla contra los recursos Apigee que dio el curso y ajustarla | `entregable-semana8.md` sección 1.4 |
| Corrida de CodeScene | Correr CodeScene sobre el repo con el incremento `api_v3` y reportar la salud del código nuevo (instrumentación de mantenibilidad declarada). Daniel tiene el tablero | Complementa la sección 5.1 del entregable |
| Video de demostración | Mostrar R1 y R2 en ejecución en el legado (5000) y en la fachada (8000), con narración. **El guion escena por escena, con los comandos exactos y la narración sugerida, está en `docs/semana-8/guion-video-demostracion.md`** (10 escenas, 8 a 10 min). Montaje previo: `EXPERIMENTO.md` de la raíz del repo, pasos 0 a 4. Subir a YouTube oculto y poner la URL | `entregable-semana8.md` sección 7 |
| Post tablero Thoughtworks | La rúbrica da 2 pts por el post del tablero colaborativo de semana 5. Verificar que exista | Tablero del curso |
| Revisión final y PDF | Revisar horas de la sección 5.2 (hoy dice 2,0 h del trabajo dirigido), quitar el bloque de estado interno del entregable y exportar a PDF para Coursera | `entregable-semana8.md` |

## 7. Estado contra la rúbrica

| Ítem de la rúbrica | Puntos | Estado |
| :--- | :--- | :--- |
| Diagrama de despliegue to-be con patrones/tácticas | 10 | LISTO (sección 1, figura reutilizada del video de avance) |
| Preguntas Apigee | 2 | BORRADOR, falta validar con los recursos del curso |
| Propósito | 2 | LISTO |
| Requisitos (n=2) | 2 | LISTO |
| Tecnología destino | 4 | LISTO |
| Mapeos con cardinalidad | 6 | LISTO |
| Ejemplos de código | 12 | LISTO (con código real del repo, legado y moderno) |
| Instrumentación y datos | 4 | LISTO (más el script ejecutado como evidencia) |
| Interesados | 2 | LISTO |
| Diseño detallado (2 UML) | 8 | LISTO |
| Unidad de estimación justificada | 4 | LISTO (con las 2 preguntas orientadoras respondidas) |
| Estimación de esfuerzo | 6 | LISTO (26 puntos) |
| Recomendaciones post-experimento | 8 | LISTO (SÍ viable, con desviaciones y recomendaciones) |
| Esfuerzo real | 4 | LISTO (2,0 h, revisar si el equipo quiere ajustar) |
| Enlace repositorio | 2 | LISTO (el código queda en el branch `experimento`, enlazado en la sección 6 del entregable) |
| Video demostración (contenido) | 16 | FALTA grabar |
| Video (formato y calidad) | 6 | FALTA grabar |
| Tablero Thoughtworks s5 | 2 | FALTA verificar |
