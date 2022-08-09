import subprocess

# Build
subprocess.run(f'cmake --build ./PragmaticPlugin/Build --config RelWithDebInfo --target PragmaticPlugin', shell=True)