#! /bin/sh

pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot web/
poedit web/translations/fr/LC_MESSAGES/messages.po
