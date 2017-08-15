import os

from yamlconfig import rootdir_logic

matching_keys = ['myfile', 'myFile', 'my_file_trails', 'someDir', 'some_dir', 'somedir']
not_matching = ['profile', '_profile', 'Profile_', 'nadir', 'Nadir_']


def test_key_matches():
    for key in matching_keys:
        assert rootdir_logic._key_matches(
                key, regex=rootdir_logic.default_key_regex, exclude=['rootdir'])


def test_join_paths_with_rootdir():
    rootdir = '/absolute/path'
    relative_path = 'relative/path'
    expected = os.path.abspath(os.path.join(rootdir, relative_path))
    all_match = {
            'rootdir': rootdir,
            'myfile': relative_path,
            'myFile': relative_path,
            'my_file_trails': relative_path,
            'someDir': relative_path,
            'some_dir': relative_path}

    joined = rootdir_logic.join_paths_with_rootdir(all_match.copy())
    for key in joined:
        print(key)
        if key == 'rootdir':
            continue
        assert joined[key] == expected


def test_remove_rootdir_from_paths():
    rootdir = os.path.abspath('/absolute/path')
    relative_path = 'relative/path'
    unjoined_dir = '/some/other/absolute/path'
    something_else = 'hello/world this has /slashes but is not a path'
    configdict = {
            'rootdir': rootdir,
            'joined_dir': os.path.abspath(os.path.join(rootdir, relative_path)),
            'unjoined_dir': unjoined_dir,
            'something_else': something_else}
    removed = configdict.copy()
    rootdir_logic.remove_rootdir_from_paths(removed)
    assert removed['joined_dir'].replace('\\', '/') == relative_path
    assert removed['something_else'] == something_else
    assert removed['unjoined_dir'] == unjoined_dir
