# -*- coding: utf-8 -*-

import click
import logging

from scripts.dc_handler import analyze


@click.command()
@click.argument('file', type=click.File("rb"), nargs=-1)
@click.option('-s', '--source', default='jira', help='-s [jira/web/cli] to choose a source')
@click.option('-f', '--folder', default='jira', help='selec')
@click.option('-n', '--name', default='jira', help='selec')
@click.option('-c', '--clear', default='jira', help='selec')
def parser(file, source):
    print(file)
    report = analyze(dc_name='cli', dc_file=file, dc_source=[source, 'CLI'])
    click.echo(report)


# Create a custom logger
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('parser.log')
console_handler.setLevel(logging.CRITICAL)
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to handlers
form = '%(asctime)s - %(levelname)s - %(pathname)s - %(message)s'
formatter = logging.Formatter(fmt=form, datefmt='%d-%b-%y %H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


if __name__ == "__main__":
    parser()
