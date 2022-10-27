# -*- coding: ascii -*-

"""Pragmatic.Pragmatic: provides entry point main()."""

from .__init__ import __version__
from .graph import get_latest_visual_graph, get_next_visual_graph, scan_directory

import os
from pathlib import Path
import json
import urllib.request
import zipfile
import hashlib
import time
import _thread as thread

import click
from flask import Flask, jsonify, render_template, Response
import pandas as pd
import numpy as np

from . import shared

# Flask server

app = Flask(__name__)

def flaskThread():
	app.run()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/miserables.json', methods=['GET'])
def get_miserables():
	data = get_latest_visual_graph()
	return jsonify(data)

def loop_visual_graphs():
	'''this could be any function that blocks until data is ready'''
	time.sleep(3.0)
	data = json.dumps(get_next_visual_graph())
	return data

def latest_visual_graph():
	while True:
		visual_graph = get_latest_visual_graph()
		if visual_graph is not None:
			return visual_graph

@app.route('/stream')
def stream():
	def eventStream():
		while True:
			# wait for source data to be available, then push it
			yield 'data: {}\n\n'.format(loop_visual_graphs())
	return Response(eventStream(), mimetype="text/event-stream")

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
	return Path(dir)

# Init

def update_progress_bar(block_num: int, block_size: int, total_size: int):
	progress = block_num * block_size
	print(f'Working [{progress}/{total_size}] [{"{:.1f}".format(100 * progress/total_size)}%]', end='\r')

def get_release(release: str, name: str, dir: Path):
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
@click.option('--server/--no-server', default=False)
def cli(server: bool):
	shared.server = server

@click.command()
def init():
	print('Initializing pragmatic')
	print('Downloading LLVM')
	get_release('llvm-14-1', 'LLVM', get_data_dir())

@click.command()
@click.argument('path', type=click.Path(exists=True))
def build(path: str):
	path = Path(path)
	# if a file was given, change path to it's directory
	if path.is_file():
		path = path.parent

	# set initial path given to pragmatic
	shared.initial_path = path
	shared.meta_path = path.joinpath(shared.META_FILE)

	# begin build
	print(f'Building {shared.initial_path}')
	scan_directory(Path(path))

# Main

def main():
	print(f'Running pragmatic version {__version__}.')


	cli.add_command(init)
	cli.add_command(build)

	try:
		cli()
	except SystemExit as err:
		# re-raise unless click.main() finished without an error
		if err.code:
			raise
	if shared.server:
		thread.start_new_thread(flaskThread, ())
		while True:
			pass