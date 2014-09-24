_config = None


def get_global_config():
    global _config

    import configlog.configurator
    if _config is None:
        _config = configlog.configurator.Configurator()
    return _config


def reset():
    global _config
    _config = None


def set(settings):
    return get_global_config().set(settings)


def get_dict_config():
    return get_global_config().get_dict_config()
