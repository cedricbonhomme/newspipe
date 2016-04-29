#! /bin/sh

pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot ..
poedit fr/LC_MESSAGES/messages.po
