import os.path
import logging
from collections import OrderedDict

import ruamel.yaml

logger = logging.getLogger(__name__)

_ruamel_type = ruamel.yaml.comments.CommentedMap
_dict_types = (dict, OrderedDict, _ruamel_type)


def set_rootdir(configdict, config_file):
    """Set rootdir in configdict"""
    if 'rootdir' not in configdict or not configdict['rootdir']:
        configdict['rootdir'] = os.path.dirname(config_file)


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


def join_paths_with_rootdir(configdict, default_rootdir=None,
        endings=['dir', 'file', 'File'], inkey=['_dir'], exclude=['rootdir']):
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
    if rootdir is None:
        return configdict
    for key in configdict:
        if isinstance(configdict[key], _dict_types):
            configdict[key] = join_paths_with_rootdir(configdict[key])
        elif _key_matches(key, endings, inkey, exclude):
            if configdict[key] is not None:
                try:
                    configdict[key] = os.path.abspath(os.path.join(rootdir, configdict[key]))
                except (TypeError, ValueError):
                    pass
    return configdict


def remove_rootdir_from_paths(configdict):
    """Reverse join_paths_with_rootdir"""
    try:
        rootdir = configdict['rootdir']
    except KeyError:
        return
    if not rootdir:
        return
    for key in configdict:
        if isinstance(configdict[key], _dict_types):
            remove_rootdir_from_paths(configdict[key])
        elif key.endswith('File') and configdict[key]:
            relpath = os.path.relpath(configdict[key], rootdir)
            if not relpath.startswith('.'):
                configdict[key] = relpath


def plain_parse_yaml(options_file):
    """Parse options file (yaml)"""
    with open(options_file, 'r') as fin:
        return ruamel.yaml.round_trip_load(fin)


def parse_config_file(configfile, join_rootdir=True, merge_linked_files=True):
    """Parse YAML config file

    Parameters
    ----------
    configfile : str
        path to YAML config file
    join_rootdir : bool
        join paths with rootdir
        if `rootdir` is not in configfile, use configfile dir
    merge_linked_files : bool
        merge other config files listed under `config_files`
    """
    configdict = plain_parse_yaml(configfile)

    if join_rootdir:
        join_paths_with_rootdir(configdict, default_rootdir=os.path.dirname(configfile))

    if merge_linked_files:
        other_configfiles = configdict.pop('config_files', [])
        for cf in other_configfiles:
            other_configdict = parse_config_file(cf)
            other_configdict.pop('rootdir', None)
            configdict.update(other_configdict)

    return configdict


def parse_merge_linked_files(configfiles, **kwargs):
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


def update_recursive(template, subset,
        ignore_notintemplate=True, delete_notinsubset=False):
    """Update template with subset, recursively, IN-PLACE!

    Parameters
    ----------
    template : mappable or _ruamel_type
        template
        will be changed in-place!
    subset : mappable
        config dict, subset of template
    ignore_notintemplate : bool
        do not add keys that are not in template
    delete_notinsubset : bool
        delete keys from template that are not in subset
        i.e. the output will contain only the intersection between
        template and subset or only subset (if ignore_notintemplate is set)
    """
    if not isinstance(template, _dict_types) or not isinstance(subset, _dict_types):
        return subset

    for key in subset:
        if key not in template and ignore_notintemplate:
            continue
        elif key in template and isinstance(template[key], _dict_types):
            update_recursive(
                    template=template[key],
                    subset=subset[key],
                    ignore_notintemplate=ignore_notintemplate,
                    delete_notinsubset=delete_notinsubset)
        else:
            template[key] = subset[key]
    if delete_notinsubset:
        delete_keys_recursive(superset=template, subset=subset)


def delete_keys_recursive(superset, subset):
    """Delete the keys in superset that are not in subset

    I.e. reduce superset to its intersection with subset based on keys

    Parameters
    ----------
    superset : mappable
        superset of subset
        will be changed in-place!
    subset : mappable
        subset of superset
    """
    for key in list(superset):
        if isinstance(superset[key], _dict_types):
            delete_keys_recursive(superset[key], subset[key])
        elif key not in subset:
            del superset[key]


def save_to_yaml(configdict, yamlfile):
    """Save configdict to yaml

    Parameters
    ----------
    configdict : dict, OrderedDict, or _ruamel_type
        configdict to save
        if not already _ruamel_type, will be converted with defaults template
    yamlfile : str
        path to save configdict to
    """
    remove_rootdir_from_paths(configdict)
    with open(yamlfile, 'w') as fout:
        ruamel.yaml.round_trip_dump(configdict, fout, default_flow_style=True, top_level_colon_align=True)


def ordered_to_unordered(somedict):
    outdict = {}
    for key in somedict:
        if isinstance(somedict[key], _dict_types):
            outdict[key] = ordered_to_unordered(somedict[key])
        else:
            outdict[key] = somedict[key]
    return outdict
