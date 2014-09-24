import collections

LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')

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


class ConfigLogError(Exception): pass


def dict_config(settings):
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {},
        'handlers': {},
        'loggers': {},
    }

    handler_key_counters = collections.defaultdict(list)

    for params in settings:
        level = params.get('level', 'INFO').upper()
        assert level in LEVELS

        formatter = params.get('formatter', 'default')
        config['formatters'][formatter] = dict(DEFAULTS['formatters'][formatter])

        handler = params.get('handler', 'console')
        handler_key_items = [handler, level.lower(), formatter]
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
                value = params.get(key, default)
                handler_params[key] = value
                if value not in handler_key_counters[key]:
                    handler_key_counters[key].append(value)
                index = handler_key_counters[key].index(value)
                if index > 0:
                    handler_key_items.append('%s%d' % (key, index+1))

        handler_key = '_'.join(handler_key_items)
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
    sentry_dsn_1 = 'http://public:secret@example.com/1'
    sentry_dsn_2 = 'http://public:secret@example.com/2'
    trans = dict_config([
        dict(logger='', level='error', file='%(here)s/logs/errors.log'),
        dict(logger='myproject', handler='console', formatter='default'),
        dict(logger='myproject', level='debug', handler='sentry', dsn=sentry_dsn_1),
        dict(logger='myproject.errors', level='error', handler='sentry', dsn=sentry_dsn_2),
        dict(logger='myproject.debug', level='debug', handler='null'),
    ])

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

    assert trans['handlers'] == expected['handlers']
    assert trans['loggers'] == expected['loggers']
    assert trans == expected
