# Guion del video de demostración (entrega final, semana 8)

> Duración objetivo: **8 a 10 minutos**. Rúbrica: demostración de los requisitos en el legado (6 pts), en la app modernizada (10 pts), formato claro (3 pts), calidad de audio e imagen (3 pts).
> Requisito del enunciado: mostrar **en EJECUCIÓN** cada requisito en el legado y su correspondencia en lo modernizado, con descripción oral detallada.
>
> **Antes de grabar:** seguir `EXPERIMENTO.md` del repo (branch `experimento`) hasta el paso 4, de modo que queden corriendo el legado en el puerto 5000 y la fachada en el puerto 8000. Los curl de este guion se corren en **Git Bash** (en PowerShell las comillas del JSON dan problemas).
> Ventanas recomendadas en pantalla: dos terminales (una para comandos, otra mostrando los servidores) y un navegador.

## Escena 1. Introducción (0:30)

*En pantalla: el repo en GitHub, branch `experimento`.*

**Narración:** "Somos el Grupo 9. Esta es la demostración del experimento de modernización de Newspipe con el patrón Strangler Fig. Vamos a mostrar los dos requisitos, la gestión de feeds y la gestión de artículos, corriendo primero en el legado Flask y luego en la aplicación modernizada con FastAPI, ambos sobre la misma base de datos PostgreSQL. El código está en el branch experimento del repositorio del equipo."

## Escena 2. El montaje (0:45)

*En pantalla: terminal.*

```bash
docker ps
```

**Narración:** "La base de datos es un PostgreSQL 16 en Docker, compartida por las dos versiones. Tenemos dos procesos corriendo: en el puerto 5000 el legado puro, la aplicación Flask sin ninguna modificación, que es nuestra línea base. Y en el puerto 8000 la fachada modernizada: un shell de FastAPI que atiende nativamente los endpoints migrados y delega todo lo demás al mismo Flask legado montado adentro."

*Mostrar rápidamente las dos terminales donde corren `flask run --port 5000` y `uvicorn asgi:app --port 8000`.*

## Escena 3. R1 en el legado (1:15)

*En pantalla: terminal con Git Bash.*

Listado de feeds en el legado:

```bash
curl -s -X GET -u admin:admin123 -H "Content-Type: application/json" \
  -d '{"limit": 10}' http://localhost:5000/api/v2.0/feeds | python -m json.tool
```

**Narración:** "Este es el requisito uno en el legado: el listado de feeds por la API versión dos. Noten un detalle: el legado exige mandar un cuerpo JSON incluso en un GET, porque el parseo de argumentos es manual y vive en common punto py, el archivo con peor salud del sistema según nuestra cartografía. Responde los dos feeds sembrados."

Creación de un feed en el legado (exige todos los campos de la whitelist):

```bash
curl -s -u admin:admin123 -H "Content-Type: application/json" -d '{
  "title": "Feed demo legado", "link": "https://example.org/demo-legado.xml",
  "description": "", "site_link": "https://example.org", "enabled": true,
  "filters": [], "last_error": "", "error_count": 0, "category_id": null
}' http://localhost:5000/api/v2.0/feed | python -m json.tool
```

**Narración:** "Y esta es la creación. Otro síntoma del contrato informal: si no mandamos todos los campos de la lista blanca, incluso los que deberían tener valores por defecto, la petición falla. Responde 201 con el feed creado."

## Escena 4. R1 en lo modernizado (1:30)

Listado por la fachada:

```bash
curl -s -u admin:admin123 "http://localhost:8000/api/v2.0/feeds?limit=10" | python -m json.tool
```

**Narración:** "El mismo requisito en la aplicación modernizada, por el puerto 8000. La URL es exactamente la misma, api slash v2.0 slash feeds, porque la fachada Strangler Fig publica los endpoints migrados bajo el mismo prefijo: los consumidores no se enteran de la migración. Aquí ya no hace falta cuerpo JSON, los parámetros son query params tipados. Y la respuesta es la misma: los mismos feeds, desde la misma base de datos."

Creación por la fachada (solo los campos obligatorios):

```bash
curl -s -u admin:admin123 -H "Content-Type: application/json" \
  -d '{"title": "Feed demo fachada", "link": "https://example.org/demo-fachada.xml"}' \
  http://localhost:8000/api/v2.0/feed | python -m json.tool
```

**Narración:** "La creación moderna solo pide título y enlace: el resto son valores por defecto declarados en el esquema Pydantic, no en código artesanal. Responde 201."

El feed creado por la fachada es visible desde el legado (misma base de datos):

```bash
curl -s -X GET -u admin:admin123 -H "Content-Type: application/json" \
  -d '{"limit": 20}' http://localhost:5000/api/v2.0/feeds | python -m json.tool | grep title
```

**Narración:** "Y la prueba de la base de datos única: consultamos otra vez el legado y el feed que acabamos de crear por la ruta moderna ya está ahí. No hay sincronización ni migración de datos, es la misma base."

## Escena 5. R2 en el legado (0:45)

```bash
curl -s -X GET -u admin:admin123 -H "Content-Type: application/json" \
  -d '{"limit": 10}' http://localhost:5000/api/v2.0/articles | python -m json.tool | head -30

curl -s -u admin:admin123 http://localhost:5000/api/v2.0/article/1 | python -m json.tool
```

**Narración:** "El requisito dos en el legado: el listado de artículos y la consulta por identificador. Responde los cuatro artículos sembrados y el artículo uno."

## Escena 6. R2 en lo modernizado (1:00)

```bash
curl -s -u admin:admin123 "http://localhost:8000/api/v2.0/articles?feed_id=1&readed=true" | python -m json.tool

curl -s -u admin:admin123 http://localhost:8000/api/v2.0/article/1 | python -m json.tool
```

**Narración:** "En la fachada, el listado soporta los filtros como parámetros tipados y declarados: por feed y por estado de lectura. Aquí pedimos los artículos del feed uno que ya están leídos. Y la consulta por identificador devuelve el mismo artículo uno que el legado. La lógica no se reescribió: los routers nuevos delegan en los mismos controllers y modelos del legado, por eso la paridad es exacta."

## Escena 7. El contrato OpenAPI (0:45)

*En pantalla: navegador en `http://localhost:8000/docs`.*

**Narración:** "Este es un beneficio directo de mantenibilidad: la documentación OpenAPI de los endpoints migrados se genera sola a partir de los esquemas. El legado no tiene nada equivalente, el contrato vivía en la cabeza del dueño del código. Desde aquí se puede probar cualquier endpoint."

*Expandir `GET /api/v2.0/feeds`, clic en Try it out, Execute (autenticarse con admin/admin123 si lo pide).*

## Escena 8. Convivencia (Strangler Fig en acción) (1:00)

*En pantalla: navegador en `http://localhost:8000/login`.*

**Narración:** "La convivencia es la clave del patrón. Esta es la interfaz web del legado servida a través de la fachada: la ruta login no está migrada, así que el shell la delega al Flask interno vía el adaptador WSGI. El usuario no nota nada."

```bash
curl -s -u admin:admin123 http://localhost:8000/api/v2.0/feed/1 | python -m json.tool
```

**Narración:** "Y dentro de la propia API: la consulta de un feed por identificador no está migrada, y aun así responde por el puerto 8000, porque la fachada la delega al legado. Podemos migrar operación por operación, sin big bang, y el legado se va reduciendo hasta desaparecer."

## Escena 9. Verificación automatizada (0:45)

```bash
.venv/Scripts/python parity_check.py
```

**Narración:** "Para cerrar, la instrumentación del experimento: dieciséis verificaciones automatizadas que comparan el legado contra la fachada. Paridad de payload campo a campo en los dos requisitos, creación por ambas rutas sobre la misma base, aislamiento por usuario, convivencia y contrato OpenAPI. Dieciséis de dieciséis exitosas."

## Escena 10. Cierre (0:30)

**Narración:** "Con esto queda demostrado el experimento: los dos requisitos operan en FastAPI con paridad funcional respecto al legado, sobre la misma base de datos y conviviendo con todo lo no migrado. La conclusión del post experimento es que la arquitectura destino sí hace viable la modernización. Gracias."

## Notas de producción

- Resolución 1080p, micrófono cercano, sin música de fondo.
- Antes de grabar hacer una pasada completa de los comandos para que las respuestas salgan sin errores y con datos limpios (si se corrió `parity_check.py` varias veces habrá feeds de prueba extra en los listados: no estorban, pero se pueden mencionar o resembrar la base bajando el volumen de Docker con `docker compose -f docker-compose-experiment.yml down -v` y repitiendo el paso 3 del runbook).
- `python -m json.tool` es solo para que el JSON salga legible en cámara.
- Subir a YouTube en modo oculto y poner la URL en la sección 7 de `docs/semana-8/entregable/entregable-semana8.md` y en Coursera.
