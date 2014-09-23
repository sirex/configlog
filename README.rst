configlog
=========

Eache to use python logging configuration with sane defaults.


Quick start
-----------

Imperative configuration:

.. code-block:: python

    import configlog

    configlog.defaults('django')
    configlog.set('', 'error', file='%(here)s/logs/errors.log')
    configlog.set('myproject', handler='console', formatter='default')
    configlog.set('myproject.errors', 'error', 'sentry')
    configlog.set('myproject.debug', level='debug', handler='null')

Declarative configuration:

.. code-block:: python

    import configlog

    configlog.configure([
        'defaults=django'
        'level=error file=%(here)s/logs/errors.log',
        'myproject handler=console formatter=default',
        'myproject.errors error sentry',
        'myproject.debug level=debug handler=null',
    ])
