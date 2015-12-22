#! /bin/sh

pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot src/web/
poedit src/web/translations/fr/LC_MESSAGES/messages.po
