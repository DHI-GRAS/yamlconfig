

def yaml_config_option(keys=None, multiple=False,
        shortflag='-c', longflag='--config', **clickkwargs):
    """Generate YAML config file option for click

    Parameters
    ----------
    keys : list of str
        top-level keys that are required to be in YAML config
    multiple : bool
        multiple instances of the option allowed
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
    from . import merge_multiple
    from .click_type import YAMLConfig

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
                try:
                    config = {k:config[k] for k in keys}
                except KeyError:
                    raise ValueError('Merged config dict does not have required keys (). Got {}.'.format(set(keys), set(config)))
            kwargs.update(config)
            return f(*args, **kwargs)

        return yaml_option(wrapped)

    return wrap_maker
