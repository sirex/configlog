import collections

from configlog.defaults import DEFAULTS
from configlog.errors import ConfigLogError

LEVELS = ('NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')


def translate(settings):
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

        if LEVELS.index(logger['level']) > LEVELS.index(level):
            logger['level'] = level

    return config
