import progressbar
import urllib.request
import os
import zipfile
import pathlib



pbar = None
def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None

def Get(name):
	# Download
	if not pathlib.Path(F'{name}.zip').exists():
		print(f'Downloading {name} build')
		urllib.request.urlretrieve(f'https://github.com/QEDengine/Pragmatic/releases/download/llvm-0.1/{name}.zip', f'{name}.zip', show_progress)
		print('Done!')
	# Unzip
	print(f'Extracting {name} build')
	with zipfile.ZipFile(f'{name}.zip', 'r') as zip_ref:
		total = len(zip_ref.filelist)
		for x, file in enumerate(zip_ref.filelist):
			zip_ref.extract(member=file, path=f'Pragmatic/data/{name}')
			show_progress(x, 1, total)
	print('Done!')