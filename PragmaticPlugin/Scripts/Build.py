import subprocess
import os
import shutil

# Set current working directory to this file's directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))
cwd = os.getcwd()
print("cwd : " + cwd)


# Build
# output = subprocess.Popen(["cmake", "--build", "./../Build", "--config", "RelWithDebInfo", "--target", "PragmaticPlugin"], stdout=subprocess.PIPE).communicate()[0]
# print(output.decode())
subprocess.run(f'cmake --build ./../Build --config RelWithDebInfo --target PragmaticPlugin', shell=True)

# Deploy
# BOTS = Tools + "/BOTS/"
# if not os.path.exists(BOTS):
# 	os.mkdir(BOTS)
# shutil.copy("../Build/PragmaticPlugin.dll", BOTS)
# shutil.copy("../Build/PragmaticPlugin.lib", BOTS)
# shutil.copy("../Build/PragmaticPlugin.pdb", BOTS)