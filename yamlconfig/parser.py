import os.path
import logging

import ruamel.yaml

logger = logging.getLogger(__name__)


def _key_matches(key, endings, inkey, exclude):
    if key in exclude:
        return False
    for ending in endings:
        if key.endswith(ending):
            logger.debug('Key \'{}\' ends with \'{}\'.'.format(key, ending))
            return True
    for substr in inkey:
        if substr in key:
            logger.debug('Found \'{}\' in key \'{}\'.'.format(substr, key))
            return True
    return False


def join_paths_with_rootdir(configdict, default_rootdir,
        endings=['_dir', '_file'], inkey=['_dir'], exclude=['rootdir']):
    """Join all relative paths in configdict with rootdir

    Parameters
    ----------
    configdict : dict
        config dictionary
    default_rootdir : str
        default rootdir
        will be used if `rootdir` not in configdict
    endings : list of str
        key endings to match
        e.g. _dir for download_dir
    inkey : list of str
        substrings to match
    exclude : list of str
        exclude these keys
    """
    rootdir = configdict.get('rootdir', default_rootdir)
    logger.debug('Rootdir is \'{}\'.'.format(rootdir))
    for key in configdict:
        if _key_matches(key, endings, inkey, exclude):
            configdict[key] = os.path.abspath(os.path.join(rootdir, configdict[key]))
    return configdict


def parse_config_file(configfile, join_rootdir=True, merge_config_files=True):
    """Parse YAML config file

    Parameters
    ----------
    configfile : str
        path to YAML config file
    join_rootdir : bool
        join paths with rootdir
        if `rootdir` is not in configfile, use configfile dir
    merge_config_files : bool
        merge other config files listed under `config_files`
    """
    with open(configfile) as fin:
        configdict = ruamel.yaml.safe_load(fin)

    if join_rootdir:
        join_paths_with_rootdir(configdict, default_rootdir=os.path.dirname(configfile))

    if merge_config_files:
        other_configfiles = configdict.pop('config_files', [])
        for cf in other_configfiles:
            other_configdict = parse_config_file(cf)
            other_configdict.pop('rootdir', None)
            configdict.update(other_configdict)

    return configdict


def parse_merge_config_files(configfiles, **kwargs):
    """Parse and merge multiple config files

    Parameters
    ----------
    configfiles : list of str
        list of config file paths
    **kwargs : additional keyword arguments
        passed to parse_config_file
    """
    configdict = {}
    for cfpath in configfiles:
        cfd = parse_config_file(cfpath, **kwargs)
        configdict.update(cfd)
    return configdict
