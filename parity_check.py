#! /usr/bin/env python
"""Functional parity checks of the modernization experiment.

Compares the legacy API (Flask, port 5000) against the Strangler Fig facade
(FastAPI, port 8000) over the same database, for the two modernized
requirements plus the coexistence of non-migrated routes.

Usage (with both servers running):
    python parity_check.py
"""
import uuid

import httpx

LEGACY = "http://localhost:5000"
FACADE = "http://localhost:8000"
ADMIN = ("admin", "admin123")
APIUSER = ("apiuser", "api123")

# Fields compared one by one between legacy and modernized payloads
FEED_FIELDS = [
    "id", "title", "description", "link", "site_link",
    "enabled", "private", "user_id", "category_id",
    "created_date", "last_retrieved",
]
ARTICLE_FIELDS = [
    "id", "entry_id", "title", "link", "content", "readed",
    "date", "retrieved_date", "user_id", "feed_id", "category_id",
]

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def get_legacy(path, auth=ADMIN, **params):
    # The legacy v2 API expects the filters in a JSON body (or query args)
    return httpx.request(
        "GET", LEGACY + path, auth=auth,
        json={"limit": 100, **params},
    )


def get_facade(path, auth=ADMIN, **params):
    return httpx.get(FACADE + path, auth=auth, params={"limit": 100, **params})


def compare_items(name, legacy_items, facade_items, fields):
    by_id_legacy = {item["id"]: item for item in legacy_items}
    by_id_facade = {item["id"]: item for item in facade_items}
    if set(by_id_legacy) != set(by_id_facade):
        check(name, False, f"ids legado={sorted(by_id_legacy)} moderno={sorted(by_id_facade)}")
        return
    diffs = []
    for obj_id, legacy_item in by_id_legacy.items():
        for field in fields:
            lv, fv = legacy_item.get(field), by_id_facade[obj_id].get(field)
            if lv != fv:
                diffs.append(f"id {obj_id} campo {field}: {lv!r} != {fv!r}")
    check(name, not diffs, "; ".join(diffs[:3]))


# ---------------------------------------------------------------- R1: feeds
r_legacy = get_legacy("/api/v2.0/feeds")
r_facade = get_facade("/api/v2.0/feeds")
check("R1 GET /feeds mismo status", r_legacy.status_code == r_facade.status_code == 200,
      f"{r_legacy.status_code} vs {r_facade.status_code}")
compare_items("R1 GET /feeds paridad de payload", r_legacy.json(), r_facade.json(), FEED_FIELDS)

# Scoping por usuario: apiuser ve exactamente lo mismo por ambas rutas
# (solo sus propios feeds, nunca los del admin)
r_legacy = get_legacy("/api/v2.0/feeds", auth=APIUSER)
r_facade = get_facade("/api/v2.0/feeds", auth=APIUSER)
ids_legacy = {f["id"] for f in r_legacy.json() or []}
ids_facade = {f["id"] for f in r_facade.json() or []}
admin_ids = {f["id"] for f in get_legacy("/api/v2.0/feeds").json() or []}
check("R1 GET /feeds scoping por usuario (apiuser solo ve lo suyo)",
      ids_legacy == ids_facade and not (ids_legacy & (admin_ids - ids_legacy)),
      f"legado={sorted(ids_legacy)} moderno={sorted(ids_facade)}")

# R1 creacion: un feed via el legado y otro via la fachada, ambos deben quedar
# en la misma base y ser visibles desde la otra ruta
run_id = uuid.uuid4().hex[:8]
new_feed_legacy = {
    "title": "Feed creado via legado", "link": f"https://example.org/{run_id}-legacy.xml",
    "description": "", "site_link": "https://example.org", "enabled": True,
    "filters": [], "last_error": "", "error_count": 0, "category_id": None,
}
r = httpx.post(LEGACY + "/api/v2.0/feed", auth=APIUSER, json=new_feed_legacy)
check("R1 POST /feed (legado) responde 201", r.status_code == 201, str(r.status_code))
legacy_created_id = r.json()["id"] if r.status_code == 201 else None

new_feed_facade = {
    "title": "Feed creado via fachada", "link": f"https://example.org/{run_id}-facade.xml",
    "site_link": "https://example.org",
}
r = httpx.post(FACADE + "/api/v2.0/feed", auth=APIUSER, json=new_feed_facade)
check("R1 POST /feed (fachada) responde 201", r.status_code == 201, str(r.status_code))
facade_created_id = r.json()["id"] if r.status_code == 201 else None

if legacy_created_id and facade_created_id:
    ids_legacy = {f["id"] for f in get_legacy("/api/v2.0/feeds", auth=APIUSER).json() or []}
    ids_facade = {f["id"] for f in get_facade("/api/v2.0/feeds", auth=APIUSER).json() or []}
    both = {legacy_created_id, facade_created_id}
    check("R1 misma BD: ambos feeds visibles por ambas rutas",
          both <= ids_legacy and both <= ids_facade,
          f"legado ve {sorted(ids_legacy)}, moderno ve {sorted(ids_facade)}")

# ------------------------------------------------------------- R2: articles
r_legacy = get_legacy("/api/v2.0/articles")
r_facade = get_facade("/api/v2.0/articles")
check("R2 GET /articles mismo status", r_legacy.status_code == r_facade.status_code == 200,
      f"{r_legacy.status_code} vs {r_facade.status_code}")
compare_items("R2 GET /articles paridad de payload", r_legacy.json(), r_facade.json(), ARTICLE_FIELDS)

# Filtros: por feed y por estado de lectura
r_legacy = get_legacy("/api/v2.0/articles", feed_id=1)
r_facade = get_facade("/api/v2.0/articles", feed_id=1)
compare_items("R2 GET /articles?feed_id=1 paridad", r_legacy.json(), r_facade.json(), ARTICLE_FIELDS)

r_legacy = get_legacy("/api/v2.0/articles", readed=True)
r_facade = get_facade("/api/v2.0/articles", readed=True)
compare_items("R2 GET /articles?readed=true paridad", r_legacy.json(), r_facade.json(), ARTICLE_FIELDS)

# Consulta por identificador
r_legacy = httpx.get(LEGACY + "/api/v2.0/article/1", auth=ADMIN)
r_facade = httpx.get(FACADE + "/api/v2.0/article/1", auth=ADMIN)
check("R2 GET /article/1 mismo status", r_legacy.status_code == r_facade.status_code == 200,
      f"{r_legacy.status_code} vs {r_facade.status_code}")
compare_items("R2 GET /article/1 paridad", [r_legacy.json()], [r_facade.json()], ARTICLE_FIELDS)

# Articulo inexistente
r_facade = httpx.get(FACADE + "/api/v2.0/article/9999", auth=ADMIN)
check("R2 GET /article/9999 responde 404 en la fachada", r_facade.status_code == 404,
      str(r_facade.status_code))

# ------------------------------------------------- convivencia (Strangler)
# Ruta NO migrada de la API v2: GET /feed/<id> debe delegarse al Flask legado
r_legacy = httpx.get(LEGACY + "/api/v2.0/feed/1", auth=ADMIN)
r_facade = httpx.get(FACADE + "/api/v2.0/feed/1", auth=ADMIN)
check("Convivencia: GET /feed/1 (no migrado) delegado al legado",
      r_legacy.status_code == r_facade.status_code == 200
      and r_legacy.json()["id"] == r_facade.json()["id"],
      f"{r_legacy.status_code} vs {r_facade.status_code}")

# Interfaz web legada a traves de la fachada
r_facade = httpx.get(FACADE + "/login", follow_redirects=True)
check("Convivencia: web legada /login servida por la fachada",
      r_facade.status_code == 200 and "newspipe" in r_facade.text.lower(),
      str(r_facade.status_code))

# Contrato OpenAPI generado
r = httpx.get(FACADE + "/openapi.json")
paths = set(r.json().get("paths", {})) if r.status_code == 200 else set()
expected = {"/api/v2.0/feeds", "/api/v2.0/feed", "/api/v2.0/articles",
            "/api/v2.0/article/{article_id}"}
check("OpenAPI generado con los 4 endpoints migrados", expected <= paths,
      f"paths={sorted(paths)}")

print()
passed = sum(1 for _, ok, _ in results if ok)
print(f"Resultado: {passed}/{len(results)} verificaciones exitosas")
