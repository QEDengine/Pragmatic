from ast import Return
import subprocess
import shutil
import glob
import os
import re
from sys import argv

os.chdir(os.path.join(os.path.dirname(__file__), '../..'))
print(f'cwd : {os.getcwd()}')

print('Incrementing version')
version = re.search(
	r'^__version__\s*=\s*"(.*)"',
	open('Pragmatic/__init__.py').read(),
	re.M
	).group(1)
version_components = version.split('.')
version_components[-1] = str(int(version_components[-1]) + 1)
new_version_string = f'__version__ = "{".".join(version_components)}"'
with open ('Pragmatic/__init__.py', 'r' ) as in_f:
	content = in_f.read()
	with open ('Pragmatic/__init__.py', 'w' ) as out_f:
		content_new = re.sub(r'^__version__\s*=\s*"(.*)"', new_version_string, content, flags = re.M)
		out_f.write(content_new)

print('Creating source distribution')
subprocess.run('python setup.py sdist')

print('Uploading distribution to PyPI')
tarball = glob.glob('dist/Pragmatic-*.*.*.tar.gz')[0]
if len(argv) == 2:
	subprocess.run(f'twine upload {tarball} -u {argv[1]} -p {argv[2]}')
else:
	subprocess.run(f'twine upload {tarball}')
