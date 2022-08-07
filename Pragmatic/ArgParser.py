# -*- coding: ascii -*-


import argparse
from .Registry import Registry

import sys

def ParseArgs():
	# Create arg parser
	parser = argparse.ArgumentParser(prog='Pragmatic')

	# Add arguments for each registered function
	for funcName, func in Registry.args.items():
		parser.add_argument(f'--{funcName}', action='store_true')

	# Parse the arguments
	parsedArgs = vars(parser.parse_args())

	# Call all registered functions for each flag
	for funcName, func in Registry.args.items():
		if (parsedArgs[funcName]):
			func()

@Registry.argument
def Test():
	print('stuff')
	pass