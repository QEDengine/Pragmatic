# -*- coding: ascii -*-

"""Pragmatic.Pragmatic: provides entry point main()."""

from .__init__ import __version__
from.graph import test

import os
import pathlib
import json
import urllib.request
import zipfile
import hashlib
import _thread as thread

import click
from flask import Flask, jsonify, render_template
import pandas as pd
import numpy as np                                          

# Flask server

incomes = [
	{
		'description': 'salary',
		'amount': 5000
	}
]
app = Flask(__name__)

def flaskThread():
    app.run()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/graph', methods=['GET'])
def get_graph():
	return jsonify(incomes)

@app.route('/miserables.json', methods=['GET'])
def get_miserables():
	data = test()
	return data

# Hash utils

def hash_file(file_path: str) -> str:
	BLOCK_SIZE = 65536
	hasher = hashlib.sha1()
	with open(file_path, 'rb') as file_handle:
		buf = file_handle.read(BLOCK_SIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = file_handle.read(BLOCK_SIZE)
	return hasher.hexdigest()

def hash_str(str: str) -> str:
	hasher = hashlib.sha1()
	hasher.update(str.encode('utf-8'))
	return hasher.hexdigest()

# Path utils

def get_data_dir():
	dir = os.path.dirname(os.path.realpath(__file__))
	return pathlib.Path(dir)

# Init

def update_progress_bar(block_num: int, block_size: int, total_size: int):
	progress = block_num * block_size
	print(f'Working [{progress}/{total_size}] [{"{:.1f}".format(100 * progress/total_size)}%]', end='\r')

def get_release(release: str, name: str, dir: pathlib.Path):
	print(f'Downloading {release} {name}.zip to dir : {str(dir)}')
	zip_file = dir.joinpath(f'{name}.zip')
	urllib.request.urlretrieve(f'https://github.com/QEDengine/Pragmatic/releases/download/{release}/{name}.zip', str(zip_file), update_progress_bar)
	print('')
	print(f'Extracting {name}.zip')
	dir.joinpath('LLVM').mkdir(exist_ok=True)
	with zipfile.ZipFile(str(zip_file), 'r') as zip_ref:
		total = len(zip_ref.filelist)
		for x, file in enumerate(zip_ref.filelist):
			zip_ref.extract(member=file, path=str(dir.joinpath('LLVM')))
			update_progress_bar(x, 1, len(zip_ref.filelist))
	print('')

	os.remove(str(zip_file))

# Commands

@click.group()
def cli():
    pass

@click.command()
def init():
	print('Initializing pragmatic')
	print('Downloading LLVM')
	get_release('llvm-14-1', 'LLVM', get_data_dir())

@click.command()
def build():
	print('Building')

# Main

def main():
	print(f"Running pragmatic version {__version__}.")
	thread.start_new_thread(flaskThread, ())

	cli.add_command(init)
	cli.add_command(build)

	try:
		cli()
	except SystemExit as err:
		# re-raise unless click.main() finished without an error
		if err.code:
			raise

	while True:
		pass