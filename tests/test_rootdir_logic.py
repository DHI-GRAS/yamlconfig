import os
import sys

import pytest

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
    joined_path = os.path.abspath(os.path.join(rootdir, relative_path))
    expected = {
        'myfile': joined_path,
        'myFile': joined_path,
        'my_file_trails': joined_path,
        'someDir': joined_path,
        'some_dir': joined_path,
        'anotherfile': 5
    }
    all_match = {
        'rootdir': rootdir,
        'myfile': relative_path,
        'myFile': relative_path,
        'my_file_trails': relative_path,
        'someDir': relative_path,
        'some_dir': joined_path,
        'anotherfile': 5
    }

    joined = rootdir_logic.join_paths_with_rootdir(all_match.copy())
    for key in joined:
        print(key)
        if key == 'rootdir':
            continue
        assert joined[key] == expected[key]


def test_join_path_list_with_rootdir():
    rootdir = '/absolute/path'
    relative_path = 'relative/path'
    joined_path = os.path.abspath(os.path.join(rootdir, relative_path))
    expected = {
        'myfile': [joined_path],
        'myFile': [joined_path] * 20,
        'someDir': [5],
        'some_dir': [5, 5],
        'anotherdir': [5, joined_path]
    }
    all_match = {
        'rootdir': rootdir,
        'myfile': [relative_path],
        'myFile': [relative_path] * 20,
        'someDir': [5],
        'some_dir': [5, 5],
        'anotherdir': [5, relative_path]
    }

    joined = rootdir_logic.join_paths_with_rootdir(all_match.copy())
    for key in joined:
        print(key)
        if key == 'rootdir':
            continue
        assert joined[key] == expected[key]


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


@pytest.mark.skipif(
    sys.platform != 'win32',
    reason="only on windows")
def test_remove_rootdir_from_paths_windows():
    before = dict(
        rootdir=r'C:\somedrive\something',
        absolute_dir=r'E:\otherdrive\something',
        relative_dir=r'.\something',
        remove_root_dir=r'C:\somedrive\something\additional')
    after = before.copy()
    rootdir_logic.remove_rootdir_from_paths(after)
    assert after['absolute_dir'] == before['absolute_dir']
    assert after['relative_dir'] == before['relative_dir']
    assert after['remove_root_dir'] == 'additional'
