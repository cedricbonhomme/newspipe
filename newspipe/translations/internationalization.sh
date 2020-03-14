#! /bin/sh

pybabel extract -F newspipe/translations/babel.cfg -k lazy_gettext -o newspipe/translations/messages.pot .
poedit newspipe/translations/fr/LC_MESSAGES/messages.po
