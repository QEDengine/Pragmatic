# -*- coding: ascii -*-


"""Pragmatic.Pragmatic: provides entry point main()."""

import os
import pathlib

from .GetRelease import GetReleaseFile
from .graph_build import Graph_build 
import click
import shutil
from .__init__ import __version__
from .FileUtils import GetDataDir

@click.group()
def cli():
    pass

@click.command()
def download():
	shutil.rmtree(GetDataDir())
	os.makedirs(GetDataDir())
	GetReleaseFile('LLVM', 'llvm-14-1')
	GetReleaseFile('PragmaticPlugin', '0.1')
	
@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True))
def build(path):
	print(f'cwd : {os.getcwd()}')
	formatted_path = click.format_filename(path)
	Graph_build.build(formatted_path)

def main():
	print(f"Running pragmatic version {__version__}.")
	
	cli.add_command(download)
	cli.add_command(build)

	cli()