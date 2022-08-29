# -*- coding: ascii -*-

"""Pragmatic.Pragmatic: provides entry point main()."""


from .__init__ import __version__
import click

@click.group()
def cli():
    pass

@click.command()
def test():
	print('test')

def main():
	print(f"Running pragmatic version {__version__}.")
	
	cli.add_command(test)

	cli()