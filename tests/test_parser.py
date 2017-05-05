import yamlconfig

import testdata


def test_parse_config_file():
    files = testdata.get_data_files()
    yamlfile = files['relative_paths']
    config = yamlconfig.parse_config_file(yamlfile)
    assert config['relative_dir'] == config['expected_relative']
    assert config['absolute_dir'] == config['expected_absolute']
    assert config['no_diir'] == config['expected_no_diir']


def test_rootdir_null():
    files = testdata.get_data_files()
    yamlfile = files['rootdir_null']
    config = yamlconfig.parse_config_file(yamlfile)
    assert config['absolute_dir'] == config['expected_absolute']
    assert config['no_diir'] == config['expected_no_diir']
