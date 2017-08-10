

def yaml_config_option(keys=None, allow_missing=False, multiple=True,
        drop_keys=None, shortflag='-c', longflag='--config', **clickkwargs):
    """Generate YAML config file option for click

    Parameters
    ----------
    keys : list of hashable or list of (hashable, default_value)
        top-level keys
        single keys are required to be in YAML config
        tuples interpreted as optional where the second
        item is used as default value
    allow_missing : bool
        allow for missing keys
    multiple : bool
        multiple instances of the option allowed
    drop_keys : list of str
        drop keys from result
    shortflag, longflag : str
        short and long option flags
    **clickkwargs : additional keyword arguments
        passed to click.option
        e.g. `required` or `help`

    Returns
    -------
    callable : decorator to use on cli function
    """
    import functools
    import click
    from yamlconfig import merge_multiple
    from yamlconfig.click_type import YAMLConfig

    configkey = '__configkey'

    yamltype = YAMLConfig()

    kw = dict(required=True, help='Config YAML file')
    kw.update(clickkwargs)
    yaml_option = click.option(
            shortflag, longflag, configkey,
            multiple=multiple, type=yamltype, **kw)

    def wrap_maker(f):

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            config = kwargs.pop(configkey)
            if multiple:
                if not isinstance(config, tuple):
                    raise ValueError('Something went wrong.')
                config = merge_multiple(config)

            if keys is not None:
                # subset config
                config_sub = {}
                for k in keys:
                    if isinstance(k, (list, tuple)) and len(k) == 2:
                        config_sub[k[0]] = config.get(k[0], k[1])
                        continue
                    try:
                        config_sub[k] = config[k]
                    except KeyError:
                        if allow_missing:
                            continue
                        else:
                            raise ValueError(
                                    'Config file(s) are missing required key \'{}\'.'.format(k))
                kwargs.update(config_sub)
            else:
                kwargs.update(config)

            if drop_keys:
                for key in drop_keys:
                    kwargs.pop(key, None)

            return f(*args, **kwargs)

        return yaml_option(wrapped)

    return wrap_maker
