import yamlconfig

import testdata


def test_parse_merge_linked_files():

    testfiles = testdata.get_data_files()
    infile = testfiles['merge_linked_linking']
    expected = yamlconfig.plain_parse_yaml(testfiles['merge_linked_expected'])
    expected = yamlconfig.ordered_to_unordered(expected)
    result = yamlconfig.parse_config_file(infile, merge_linked_files=True)
    assert yamlconfig.ordered_to_unordered(result) == expected
