import logging.config

import configlog.errors as errors
import configlog.parser as parser
import configlog.translators.dictconfig as dictconfig


class Configurator(object):
    def __init__(self, settings=None):
        self.settings = self.norm(settings)

    def norm(self, settings):
        if settings is None:
            return []
        elif isinstance(settings, (tuple, list)):
            return list(map(self.item_norm, settings))
        elif isinstance(settings, basestring):
            return [parser.parse(settings)]
        elif isinstance(settings, dict):
            return [settings]
        else:
            raise errors.ConfigLogError(
                'Unknown settings type %r.' % type(settings)
            )

    def item_norm(self, item):
        if isinstance(item, basestring):
            return parser.parse(item)
        elif isinstance(item, dict):
            return item
        else:
            raise errors.ConfigLogError(
                'Unknown settings type %r.' % type(item)
            )

    def set(self, settings):
        self.settings.extend(self.norm(settings))
        return self

    def configure(self, settings=None):
        self.log(settings)
        dict_config = self.get_dict_config()
        logging.config.dictConfig(dict_config)

    def get_dict_config(self):
        return dictconfig.translate(self.settings)
