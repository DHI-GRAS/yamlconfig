import os
import re
import logging
from collections import OrderedDict

import ruamel.yaml

logger = logging.getLogger(__name__)

_ruamel_type = ruamel.yaml.comments.CommentedMap
_dict_types = (dict, OrderedDict, _ruamel_type)

default_key_regex = [
        '.*_(file|dir)($|_.*)',
        '.*(File|Dir)($|_.*)',
        '.*(?<![Pp]ro)file($|_.*)',
        '.*(?<![Nn]a)dir($|_.*)']


def set_rootdir(configdict, config_file):
    """Set rootdir in configdict"""
    if 'rootdir' not in configdict or not configdict['rootdir']:
        configdict['rootdir'] = os.path.dirname(config_file)


def _key_matches(key, regex, exclude):
    if key in exclude:
        return False
    for rr in regex:
        if re.match(rr, key) is not None:
            logger.debug('Regex \'%s\' matches key \'%s\'.', rr, key)
            return True
    return False


def join_paths_with_rootdir(
        configdict,
        default_rootdir=None,
        regex=default_key_regex,
        exclude=None):
    """Join all relative paths in configdict with rootdir

    Parameters
    ----------
    configdict : dict
        config dictionary
    default_rootdir : str
        default rootdir
        will be used if `rootdir` not in configdict
    regex : list of str
        regex to match
    exclude : list of str
        exclude these keys
    """
    if exclude is None:
        exclude = ['rootdir']
    else:
        exclude.append('rootdir')

    if regex is None:
        regex = []

    rootdir = configdict.get('rootdir', default_rootdir)
    logger.debug('Rootdir is \'%s\'.', rootdir)

    if rootdir is None:
        return configdict

    for key in configdict:
        if isinstance(configdict[key], _dict_types):
            configdict[key] = join_paths_with_rootdir(
                    configdict[key],
                    default_rootdir=default_rootdir,
                    exclude=exclude)
        elif _key_matches(key, regex, exclude):
            val = configdict[key]
            if val is None:
                continue

            if isinstance(val, str):
                configdict[key] = _join_maybe(rootdir, val)
                continue

            try:
                iter(val)
            except TypeError:
                continue

            configdict[key] = [_join_maybe(rootdir, f) for f in val]

    return configdict


def _join_maybe(root, path):
    try:
        return os.path.abspath(os.path.join(root, path))
    except (TypeError, ValueError, AttributeError):
        return path


def remove_rootdir_from_paths(configdict, regex=default_key_regex, exclude=None):
    """Reverse join_paths_with_rootdir"""
    try:
        rootdir = os.path.abspath(configdict['rootdir'])
    except KeyError:
        return
    if not rootdir:
        return
    if exclude is None:
        exclude = ['rootdir']
    else:
        exclude.append('rootdir')
    for key in configdict:
        if isinstance(configdict[key], _dict_types):
            remove_rootdir_from_paths(configdict[key])
        elif _key_matches(key, regex, exclude) and configdict[key]:
            try:
                # this can fail if the paths are on different drives
                # on Windows
                relpath = os.path.relpath(configdict[key], rootdir)
            except ValueError:
                continue
            if not relpath.startswith('.'):
                configdict[key] = relpath
