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
export NEWSPIPE_CONFIG=/newspipe/instance/config.py
export FLASK_APP=runserver.py
export FLASK_ENV=development
poetry run flask db_create >/dev/null
poetry run flask create_admin --nickname admin --password password >/dev/null
poetry run pybabel compile -d newspipe/translations
poetry run flask run
