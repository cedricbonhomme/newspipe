#!/bin/sh

# Used for Docker.

set -e

shift

until (! command -v psql || PGPASSWORD=password psql -h db -U "postgres" -c '\q' )
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
export Newspipe_CONFIG=/newspipe/instance/production.py
poetry run ./manager.py db_create >/dev/null
poetry run pybabel compile -d newspipe/translations
poetry run ./runserver.py
