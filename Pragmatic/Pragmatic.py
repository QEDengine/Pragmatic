# -*- coding: ascii -*-


"""Pragmatic.Pragmatic: provides entry point main()."""


__version__ = "0.0.2"

from . import Stuff
from .Registry import Registry
from .ArgParser import ParseArgs, Test


def Main():
	print(f"Running pragmatic version {__version__}.")

	ParseArgs()