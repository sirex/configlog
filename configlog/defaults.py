DEFAULTS = {
    'formatters': {
        'default': {
            'format': '%(message)s',
        }
    },
    'handlers': {
        'null': {
            'template': {
                'class': 'logging.NullHandler',
            },
            'params': [],
        },
        'console': {
            'template': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'params': [
                ('formatter', None),
            ],
        },
        'sentry': {
            'template': {
                'class': 'raven.handlers.logging.SentryHandler',
            },
            'params': [
                ('dsn', None),
            ],
        },
    },
}
