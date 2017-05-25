import click

from . import parse_config_file
from .postproc import check_required_keys
from .postproc import RequiredKeysError


class YAMLConfig(click.ParamType):

    name = 'yamlconfig'

    def __init__(self, required_keys=None, squeeze=False):
        """YAML config file to dict

        Parameters
        ----------
        required_keys : list of str
            keys that must be in the top level of the config dict
            or the squeezed level
        squeeze : bool
            squeeze single-key top level from config dict
        """
        self.required_keys = required_keys
        self.squeeze = squeeze

    def convert(self, value, param, ctx):
        try:
            configkw = parse_config_file(value)
        except IOError as exc:
            self.fail(str(exc), param, ctx)
        except Exception as exc:
            self.fail('Unable to parse YAML from \'{}\' ({}).'.format(value, exc), param, ctx)
        if self.squeeze and len(configkw) == 1:
            configkw = configkw[list(configkw)[0]]
        try:
            check_required_keys(configkw, required_keys=self.required_keys)
        except RequiredKeysError as exc:
            self.fail(str(exc), param, ctx)
        return configkw