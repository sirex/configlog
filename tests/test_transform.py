LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')

DEFAULTS = {
    'formatters': {
        'default': {
            'format': '%(message)s',
        }
    },
    'handlers': {
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


class ConfigLogError(Exception): pass


def dict_config(settings):
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {},
        'handlers': {},
        'loggers': {},
    }

    for params in settings:
        level = params.get('level', 'INFO').upper()
        assert level in LEVELS

        formatter = params.get('formatter', 'default')
        config['formatters'][formatter] = dict(DEFAULTS['formatters'][formatter])

        handler = params.get('handler', 'console')
        handler_key = '_'.join([handler, level.lower(), formatter])
        handler_params = {}
        for key, default in DEFAULTS['handlers'][handler]['params']:
            if key == 'formatter':
                handler_params[key] = formatter
            else:
                if default is None and key not in params:
                    raise ConfigLogError((
                        'Error while configuring logger for "{logger}". '
                        '"{handler}" requires "{param}" parameter to be set.'
                    ).format(
                        logger=params['logger'],
                        handler=handler,
                        param=key,
                    ))
                handler_params[key] = params[key]
        config['handlers'][handler_key] = dict(
            DEFAULTS['handlers'][handler]['template'],
            level=level, **handler_params
        )

        if params['logger'] == '':
            if 'root' not in config:
                config['root'] = {
                    'handlers': [],
                    'level': level,
                }
            logger = config['root']
        else:
            if params['logger'] not in config['loggers']:
                config['loggers'][params['logger']] = {
                    'handlers': [],
                    'level': level,
                }
            logger = config['loggers'][params['logger']]

        logger['handlers'].append(handler_key)

        if LEVELS.index(logger['level']) < LEVELS.index(level):
            logger['level'] = level

    return config



def test_dict_config():
    trans = dict_config([
        dict(logger='', level='error', file='%(here)s/logs/errors.log'),
        dict(logger='myproject', handler='console', formatter='default'),
        dict(logger='myproject', level='debug', handler='sentry',
             dsn='http://public:secret@example.com/1'),
    ])
    assert trans == {
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
        },
        'root': {
            'handlers': ['console_error_default'],
            'level': 'ERROR'
        },
        'loggers': {
            'myproject': {
                'handlers': ['console_info_default', 'sentry_debug_default'],
                'level': 'DEBUG'
            }
        },
    }
