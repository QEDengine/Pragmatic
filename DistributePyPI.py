import subprocess
import os
import glob

print('Creating source distribution')
subprocess.run('python setup.py sdist')

print('Uploading distribution to PyPI')
tarball = glob.glob('dist/Pragmatic-*.*.*.tar.gz')[0]
subprocess.run(f'twine upload {tarball}')

print('Deleting distribution files')
dirs_to_remove = ['build', 'dist', 'Pragmatic.egg-info']
for dir in dirs_to_remove:
	os.rmdir(dir)