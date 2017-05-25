import yamlconfig

import testdata


def test_parse_merge_multiple_files():
    testfiles = testdata.get_data_files()
    infiles = [testfiles[k] for k in ['merge_multi1', 'merge_multi2']]
    expfile = testfiles['merge_multi_expected']

    expected_unordered = yamlconfig.ordered_to_unordered(
            yamlconfig.plain_parse_yaml(expfile))

    result = yamlconfig.parse_merge_multiple_files(infiles)

    assert yamlconfig.ordered_to_unordered(result) == expected_unordered
