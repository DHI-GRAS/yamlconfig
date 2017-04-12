import click


config_files_option = click.option(
        '--config-file', '-c', 'config_files',
        multiple=True, required=True,
        type=click.Path(file_okay=True), help='Config files')
