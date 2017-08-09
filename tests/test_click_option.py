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
    result = runner.invoke(main, inp)
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
    result = runner.invoke(main, inp)
    assert result.exit_code == 0
    assert result.output == 'hello world\n'


def test_drop_keys():
    testfiles = testdata.get_data_files()
    inp = ['-c', testfiles['hello_world']]

    @click.command()
    @yaml_config_option(
            keys=['name', 'greeting'], drop_keys=['name'], multiple=False)
    def main(**kwargs):
        click.echo(len(kwargs))

    runner = CliRunner()
    result = runner.invoke(main, inp)
    assert result.exit_code == 0
    assert result.output == '1\n'
