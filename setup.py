# -*- coding: ascii -*-


"""setup.py: setuptools control."""


import sys
import os
import re
import atexit
from setuptools import setup
from setuptools.command.install import install


# Read version from Pragmatic.py
version = re.search(
	'^__version__\s*=\s*"(.*)"',
	open('Pragmatic/Pragmatic.py').read(),
	re.M
	).group(1)

# Use README.md as long description
with open("README.md", "rb") as f:
	long_descr = f.read().decode("utf-8")

# Post install script hook
class CustomInstall(install):
	def run(self):
		def post_install():
			def find_module_path():
				for p in sys.path:
					if os.path.isdir(p) and 'Pragmatic' in os.listdir(p):
						return os.path.join(p, 'Pragmatic')
			install_path = find_module_path()

			print(f'Post install : {install_path}')

		atexit.register(post_install)
		install.run(self)

# Setuptools setup
setup(
	name = "Pragmatic",
	packages = ["Pragmatic"],
	entry_points =
	{
		"console_scripts": ['Pragmatic = Pragmatic.Pragmatic:Main']
	},
	cmdclass={'install': CustomInstall},
	version = version,
	description = "Python command line application bare bones template.",
	long_description = long_descr,
	long_description_content_type='text/markdown',
	author = "Szoke Balazs",
	author_email = "bala.szoke@gmail.com",
	url = "https://github.com/QEDengine",
	)