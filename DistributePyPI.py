import subprocess

import glob

tarball = glob.glob('dist/Pragmatic-*.*.*.tar.gz')[0]
subprocess.run(f'twine upload {tarball}')