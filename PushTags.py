import subprocess
from subprocess import PIPE

proc = subprocess.run(f'git push origin --tags', shell=True, stdout=PIPE)


