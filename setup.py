
from setuptools import setup

setup(
	name="pragmatic",
	version='0.0.1',
	entry_points =
	{
		"console_scripts": ['Pragmatic = pragmatic.pragmatic:main']
	},
	packages = ['pragmatic'],
	package_dir={'pragmatic': 'pragmatic'},
	package_data={'pragmatic': ['pragmatic_plugin/**']},
	install_requires = [
		'click',
	],
)