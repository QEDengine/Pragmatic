import subprocess
import os
import shutil

# Set current working directory to this file's directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))
cwd = os.getcwd()
print("cwd : " + cwd)

# Folders
Tools = "../../../../Tools"
CMakeBuild = "../../../../Build"

# Build
output = subprocess.Popen([Tools + "/CMake/bin/cmake.exe", "--build", CMakeBuild, "--config", "RelWithDebInfo", "--target", "PragmaticPlugin"], stdout=subprocess.PIPE).communicate()[0]
print(output.decode())

# Deploy
BOTS = Tools + "/BOTS/"
if not os.path.exists(BOTS):
	os.mkdir(BOTS)
shutil.copy("../Build/PragmaticPlugin.dll", BOTS)
shutil.copy("../Build/PragmaticPlugin.lib", BOTS)
shutil.copy("../Build/PragmaticPlugin.pdb", BOTS)