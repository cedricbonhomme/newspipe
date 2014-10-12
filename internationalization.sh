#! /bin/sh

pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot pyaggr3g470r/
poedit pyaggr3g470r/translations/fr/LC_MESSAGES/messages.po
