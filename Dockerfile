FROM python:3.8-alpine

RUN apk update && \
  apk add \
  build-base \
  curl \
  git \
  libffi-dev \
  openssl-dev \
  libxml2-dev \
  libxslt-dev \
  libpq \
  postgresql-dev \
  sqlite-dev \
  sqlite \
  sqlite-libs \
  npm
RUN pip install poetry

WORKDIR newspipe

COPY newspipe newspipe/
COPY instance instance/
COPY manager.py .
COPY runserver.py .
COPY package.json .
COPY package-lock.json .
COPY pyproject.toml .
COPY poetry.lock .
COPY instance/sqlite.py .
COPY instance/sqlite.py instance/
COPY instance/sqlite.py newspipe/

RUN npm install
COPY node_modules newspipe/static/npm_components

ENV Newspipe_CONFIG sqlite.py

RUN poetry install
RUN poetry run pybabel compile -d newspipe/translations
RUN poetry run ./manager.py db_create
RUN poetry run ./manager.py create_admin admin password
