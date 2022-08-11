# -*- coding: ascii -*-


"""Pragmatic.Pragmatic: provides entry point main()."""


__version__ = "0.0.19"

import imp
import os
import pathlib

from numpy import true_divide
from .GetRelease import Get
from .graph_build import graph_build 
import click

def GetDataDir():
	dir = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(dir, 'data')

@click.group()
def cli():
    pass

@click.command()
def download():
	if (not pathlib.Path(GetDataDir()).exists()):
		os.makedirs(GetDataDir())
		Get('LLVM', 'llvm-0.1')
		Get('PragmaticPlugin', '0.1')

@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True))
def build(path):
	print(f'cwd : {os.getcwd()}')
	formatted_path = click.format_filename(path)
	ii = graph_build.preprocess_file(formatted_path)
	o = graph_build.build_file(ii)
	objs = []
	objs.append(o)
	graph_build.link(objs)

def main():
	print(f"Running pragmatic version {__version__}.")
	
	cli.add_command(download)
	cli.add_command(build)

	cli()