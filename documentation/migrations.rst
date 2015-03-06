Migrations
==========

Migrations of the database are managed
with the database migrations tool
`Alembic <https://bitbucket.org/zzzeek/alembic>`_.

The Flask extensions `Flask-Script <https://github.com/smurfix/flask-script>`_
and `Flask-Migrate <https://github.com/miguelgrinberg/flask-migrate/>`_
are used to ease remote migrations.

Local migrations
----------------

.. code-block:: bash

    $ python manager.py db upgrade

Remote migrations
-----------------

.. code-block:: bash

    $ heroku run python manager.py db upgrade
