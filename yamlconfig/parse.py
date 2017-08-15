import os.path
import copy
import logging
from collections import OrderedDict

import ruamel.yaml

from yamlconfig import rootdir_logic

logger = logging.getLogger(__name__)

_ruamel_type = ruamel.yaml.comments.CommentedMap
_dict_types = (dict, OrderedDict, _ruamel_type)


def plain_parse_yaml(configfile, round_trip=False):
    """Parse YAML config file

    Parameters
    ----------
    configfile : str
        path to YAML file
    round_trip : bool
        use round-trip loader (preserves comments and spacing)
    """
    with open(configfile, 'r') as fin:
        if round_trip:
            return ruamel.yaml.round_trip_load(fin)
        else:
            return ruamel.yaml.safe_load(fin)


def parse_config_file(
        configfile, join_rootdir=False,
        merge_linked_files=True, round_trip=False,
        rootdir_kwargs={}):
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
    round_trip : bool
        use round-trip loader (preserves comments and spacing)
    rootdir_kwargs : dict
        keyword arguments passed
        to join_paths_with_rootdir
    """
    configdict = plain_parse_yaml(configfile, round_trip=round_trip)

    if join_rootdir or rootdir_kwargs:
        rootdir_logic.join_paths_with_rootdir(
                configdict, default_rootdir=os.path.dirname(configfile), **rootdir_kwargs)

    rootdir = configdict.get('rootdir', os.path.dirname(configfile))

    # pop linked files
    other_configfiles = configdict.pop('config_files', [])

    if merge_linked_files and other_configfiles:
        configdict_rules = copy.deepcopy(configdict)
        for cf in other_configfiles[::-1]:
            if rootdir is not None:
                cfpath = os.path.join(rootdir, cf)
            else:
                cfpath = cf
            other_configdict = parse_config_file(
                    cfpath,
                    join_rootdir=join_rootdir,
                    merge_linked_files=merge_linked_files,
                    round_trip=round_trip,
                    rootdir_kwargs=rootdir_kwargs)
            other_configdict.pop('rootdir', None)
            update_recursive_plain(configdict, other_configdict)

        # make sure original config dict rules
        update_recursive_plain(configdict, configdict_rules)

    return configdict


def parse_merge_multiple(configfiles, **kwargs):
    """Parse and merge multiple config files

    Parameters
    ----------
    configfiles : list of str
        list of config file paths
    **kwargs : additional keyword arguments
        passed to parse_config_file

    Returns
    -------
    dict-like
        merged config dict (last file rules)
    """
    dd = (parse_config_file(cfpath, **kwargs) for cfpath in configfiles)
    configdict = merge_multiple(dd)
    return configdict


def merge_multiple(configdicts):
    """Merge multiple config dicts

    Parameters
    ----------
    configdicts : iterable of dicts
        config dicts to merge (can be iterator)

    Returns
    -------
    dict-like
        merged config dicts
        last dict rules for values
        first dict rules for format (if ruamel type)
    """
    cfd = None
    for newcfd in configdicts:
        if cfd is None:
            cfd = copy.deepcopy(newcfd)
        else:
            update_recursive_plain(cfd, newcfd)
    return cfd


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
        if key not in subset:
            del superset[key]
        elif isinstance(superset[key], _dict_types):
            delete_keys_recursive(superset[key], subset[key])
        else:
            continue


def update_recursive_plain(template, other):
    """Wrapper for update_recursive without magic"""
    update_recursive(template, other,
            ignore_notintemplate=False, delete_notinsubset=False)


def save_to_yaml(configdict, yamlfile, **kwargs):
    """Save configdict to yaml

    Parameters
    ----------
    configdict : dict, OrderedDict, or _ruamel_type
        configdict to save
        if not already _ruamel_type, will be converted with defaults template
    yamlfile : str
        path to save configdict to
    **kwargs : additional keyword arguments
        passed to ruamel.yaml.round_trip_dump
    """
    rootdir_logic.remove_rootdir_from_paths(configdict)
    with open(yamlfile, 'w') as fout:
        ruamel.yaml.round_trip_dump(configdict, fout, default_flow_style=True, **kwargs)


def ordered_to_unordered(d):
    """Convert ordered dict to normal dict"""
    outdict = {}
    for key in d:
        if isinstance(d[key], _dict_types):
            outdict[key] = ordered_to_unordered(d[key])
        else:
            outdict[key] = d[key]
    return outdict
