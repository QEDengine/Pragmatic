# -*- coding: ascii -*-


"""Pragmatic.Pragmatic: provides entry point main()."""


__version__ = "0.0.19"

import imp
import os
import pathlib

from .GetRelease import Get
from .graph_build import Graph_build 
import click
import shutil

def GetDataDir():
	dir = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(dir, 'data')

@click.group()
def cli():
    pass

@click.command()
def download():
	shutil.rmtree(GetDataDir())
	os.makedirs(GetDataDir())
	Get('LLVM', 'llvm-14-1')
	Get('PragmaticPlugin', '0.1')
	
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