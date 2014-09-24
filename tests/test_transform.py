import configlog


def test_dict_config():
    sentry_dsn_1 = 'http://public:secret@example.com/1'
    sentry_dsn_2 = 'http://public:secret@example.com/2'

    configlog.set([
        'level=error file=%(here)s/logs/errors.log',
        'myproject handler=console formatter=default',
        'myproject level=debug handler=sentry dsn=%s' % sentry_dsn_1,
        'myproject.errors level=error handler=sentry dsn=%s' % sentry_dsn_2,
        'myproject.debug level=debug handler=null',
    ])
    dict_config = configlog.get_dict_config()
    configlog.reset()

    expected = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'default': {
                'format': '%(message)s'
            }
        },
        'handlers': {
            'console_info_default': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'stream': 'ext://sys.stdout'
            },
            'console_error_default': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'stream': 'ext://sys.stdout'
            },
            'sentry_debug_default': {
                'class': 'raven.handlers.logging.SentryHandler',
                'dsn': 'http://public:secret@example.com/1',
                'level': 'DEBUG',
            },
            'sentry_error_default_dsn2': {
                'class': 'raven.handlers.logging.SentryHandler',
                'dsn': 'http://public:secret@example.com/2',
                'level': 'ERROR',
            },
            'null_debug_default': {
                'class': 'logging.NullHandler',
                'level': 'DEBUG',
            },
        },
        'root': {
            'handlers': ['console_error_default'],
            'level': 'ERROR',
        },
        'loggers': {
            'myproject': {
                'handlers': ['console_info_default', 'sentry_debug_default'],
                'level': 'DEBUG',
            },
            'myproject.errors': {
                'handlers': ['sentry_error_default_dsn2'],
                'level': 'ERROR',
            },
            'myproject.debug': {
                'handlers': ['null_debug_default'],
                'level': 'DEBUG',
            },
        },
    }

    assert dict_config['handlers'] == expected['handlers']
    assert dict_config['loggers'] == expected['loggers']
    assert dict_config == expected
