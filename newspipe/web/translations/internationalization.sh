#! /bin/sh

pybabel extract -F newspipe/web/translations/babel.cfg -k lazy_gettext -o newspipe/web/translations/messages.pot newspipe/web/
poedit newspipe/web/translations/fr/LC_MESSAGES/messages.po
