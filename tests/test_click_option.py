import pytest
import click
from click.testing import CliRunner

from yamlconfig.click_option import yaml_config_option

import testdata


def test_multiple():

    testfiles = testdata.get_data_files()
    inp = []
    for k in ['hello', 'world']:
        inp += ['-c', testfiles[k]]

    @click.command()
    @yaml_config_option(keys=['name', 'greeting'], multiple=True)
    def main(**kwargs):
        click.echo('{greeting} {name}'.format(**kwargs))

    runner = CliRunner()
    result = runner.invoke(main, inp, catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == 'hello world\n'


def test_single():

    testfiles = testdata.get_data_files()
    inp = ['-c', testfiles['hello_world']]

    @click.command()
    @yaml_config_option(keys=['name', 'greeting'], multiple=False)
    def main(**kwargs):
        click.echo('{greeting} {name}'.format(**kwargs))

    runner = CliRunner()
    result = runner.invoke(main, inp, catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == 'hello world\n'


def test_drop_keys():
    testfiles = testdata.get_data_files()
    inp = ['-c', testfiles['hello_world']]

    @click.command()
    @yaml_config_option(
            keys=['name', 'greeting'], drop_keys=['name'])
    def main(**kwargs):
        click.echo(len(kwargs))

    runner = CliRunner()
    result = runner.invoke(main, inp, catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == '1\n'


def test_missing():

    testfiles = testdata.get_data_files()
    inp = ['-c', testfiles['hello_world']]

    @click.command()
    @yaml_config_option(
            keys=['flowers_gone'], allow_missing=False)
    def main(**kwargs):
        click.echo(len(kwargs))

    runner = CliRunner()
    with pytest.raises(ValueError):
        result = runner.invoke(main, inp, catch_exceptions=False)
        assert result.exit_code == -1


def test_keys_with_defaults():
    testfiles = testdata.get_data_files()
    inp = ['-c', testfiles['hello']]

    @click.command()
    @yaml_config_option(
            keys=[('name', 'tough guy'), 'greeting'])
    def main(**kwargs):
        click.echo('{greeting} {name}'.format(**kwargs))

    runner = CliRunner()
    result = runner.invoke(main, inp, catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == 'hello tough guy\n'
