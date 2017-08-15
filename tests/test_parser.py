import copy

import yamlconfig

import testdata


def test_parse_config_file():
    testfiles = testdata.get_data_files()
    yamlfile = testfiles['relative_paths']
    config = yamlconfig.parse_config_file(yamlfile, join_rootdir=True)
    assert config['relative_dir'] == config['expected_relative']
    assert config['absolute_dir'] == config['expected_absolute']
    assert config['no_diir'] == config['expected_no_diir']


def test_rootdir_null():
    testfiles = testdata.get_data_files()
    yamlfile = testfiles['rootdir_null']
    config = yamlconfig.parse_config_file(yamlfile, join_rootdir=True)
    assert config['absolute_dir'] == config['expected_absolute']
    assert config['no_diir'] == config['expected_no_diir']


def test_update_recursive_ignore():
    testfiles = testdata.get_data_files()

    testconfig = {}
    for key in [
            'template',
            'subset',
            'expected_ignorenotintemplate']:
        filekey = 'nested_multi_' + key
        yamlfile = testfiles[filekey]
        testconfig[key] = yamlconfig.parse_config_file(yamlfile)

    to_update = copy.deepcopy(testconfig['template'])
    yamlconfig.update_recursive(
            template=to_update,
            subset=testconfig['subset'],
            ignore_notintemplate=True,
            delete_notinsubset=False)
    expected = testconfig['expected_ignorenotintemplate']
    assert to_update == expected


def test_update_recursive_noignore():
    testfiles = testdata.get_data_files()

    testconfig = {}
    for key in [
            'template',
            'subset',
            'expected_noignorenotintemplate']:
        filekey = 'nested_multi_' + key
        yamlfile = testfiles[filekey]
        testconfig[key] = yamlconfig.parse_config_file(yamlfile)

    to_update = copy.deepcopy(testconfig['template'])
    yamlconfig.update_recursive(
            template=to_update,
            subset=testconfig['subset'],
            ignore_notintemplate=False,
            delete_notinsubset=False)
    expected = yamlconfig.ordered_to_unordered(testconfig['expected_noignorenotintemplate'])
    to_update_dict = yamlconfig.ordered_to_unordered(to_update)
    assert to_update_dict == expected


def test_update_recursive_ignore_delete():
    testfiles = testdata.get_data_files()

    testconfig = {}
    for key in [
            'template',
            'subset',
            'expected_deletenotinsubset']:
        filekey = 'nested_multi_' + key
        yamlfile = testfiles[filekey]
        testconfig[key] = yamlconfig.parse_config_file(yamlfile)

    to_update = copy.deepcopy(testconfig['template'])
    yamlconfig.update_recursive(
            template=to_update,
            subset=testconfig['subset'],
            ignore_notintemplate=True,
            delete_notinsubset=True)
    expected = testconfig['expected_deletenotinsubset']
    assert to_update == expected
