logtool
=======

A tool to make python logging configuration easier.


Quick start
-----------

Configure logging::

    import logtool

    logtool.log('myproject', level='info', handler='console', formatter='default')
    logtool.log('myproject.mymodule', 'error', 'sentry')
    logtool.ignore('myproject.mymodule', level='debug')

Show stats for loggers::

    logtool.stats()

Show tree of all available loggers::

    logtool.loggers()

