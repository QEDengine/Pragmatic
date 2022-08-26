# -*- coding: ascii -*-


"""setup.py: setuptools control."""

import re
from setuptools import setup, find_packages

# Read version from Pragmatic.py
version = re.search(
	r'^__version__\s*=\s*"(.*)"',
	open('Pragmatic/__init__.py').read(),
	re.M
	).group(1)

# Use README.md as long description
with open("README.md", "rb") as f:
	long_descr = f.read().decode("utf-8")

# Setuptools setup
setup(
	name = "Pragmatic",
	packages = ["Pragmatic"],
	entry_points =
	{
		"console_scripts": ['Pragmatic = Pragmatic.Pragmatic:main']
	},
	version = version,
	description = "Python command line application bare bones template.",
	# packages = find_packages(),
	long_description = long_descr,
	long_description_content_type='text/markdown',
	author = "Szoke Balazs",
	author_email = "bala.szoke@gmail.com",
	url = "https://github.com/QEDengine"
	)