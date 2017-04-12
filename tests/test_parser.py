from yamlconfig import parser

import testdata


def test_parse_config_file():
    files = testdata.get_data_files()
    config = parser.parse_config_file(files['relative_paths'])
    assert config['relative_dir'] == config['expected_relative']
    assert config['absolute_dir'] == config['expected_absolute']
    assert config['no_diir'] == config['expected_no_diir']
