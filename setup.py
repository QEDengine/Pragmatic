import os
import shutil
import pathlib
import urllib.request
import zipfile
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install_egg_info import install_egg_info

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

	os.remove(str(zip_file))

class CMakeExtension(Extension):
	def __init__(self, name, **kwa):
		Extension.__init__(self, name, sources=[], **kwa)

class cmake_build_ext(build_ext):
	def build_extensions(self):
		import subprocess

		# temp, ext_build dir
		if len(self.extensions) == 0:
			return
		extdir = pathlib.Path(self.get_ext_fullpath(self.extensions[0].name))
		extdir.mkdir(parents=True, exist_ok=True)

		pragmatic_build_dir: pathlib.Path = extdir.parent.joinpath('pragmatic')
		pragmatic_plugin_build_dir = pragmatic_build_dir.joinpath('pragmatic_plugin/build')
		pragmatic_plugin_build_dir.mkdir(parents=True, exist_ok=True)

		# Get clang
		get_release('llvm-14-1', 'LLVM', pragmatic_build_dir)

		# Ensure that CMake is present and working
		try:
			out = subprocess.check_output(['cmake', '--version'])
			print(out.decode('ascii'))
		except OSError:
			raise RuntimeError('Cannot find CMake executable')

		for ext in self.extensions:
			print('Building native module : ' + ext.name)

			cwd = pathlib.Path().absolute()

			build_temp = pathlib.Path(self.build_temp)
			build_temp.mkdir(parents=True, exist_ok=True)
			extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
			extdir.mkdir(parents=True, exist_ok=True)

			# example of cmake args
			config = 'RelWithDebInfo'
			cmake_args = [
				'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + str(extdir.parent.absolute())
			]

			# example of build args
			build_args = [
				'--config', config,
			]

			os.chdir(str(build_temp))
			self.spawn(['cmake', str(cwd.joinpath('pragmatic').joinpath(ext.name))] + cmake_args)
			if not self.dry_run:
				self.spawn(['cmake', '--build', '.'] + build_args)
			os.chdir(str(cwd))


			print("Installing built native module")
			shutil.copyfile(build_temp.joinpath('RelWithDebInfo').joinpath('PragmaticPlugin.dll'), pragmatic_plugin_build_dir.joinpath('PragmaticPlugin.dll'))
			shutil.copyfile(build_temp.joinpath('RelWithDebInfo').joinpath('PragmaticPlugin.pdb'), pragmatic_plugin_build_dir.joinpath('PragmaticPlugin.pdb'))



			# Troubleshooting: if fail on line above then delete all possible 
			# temporary CMake files including "CMakeCache.txt" in top level dir.

class cmake_egg_info(install_egg_info):
	def run(self):
		self.outputs.append()
		super().run(self)


setup(
	name="pragmatic",
	version='0.0.1',
	entry_points =
	{
		"console_scripts": ['Pragmatic = Pragmatic.Pragmatic:main']
	},
	packages = ['pragmatic'],
	package_dir={'pragmatic': 'pragmatic'},
	package_data={'pragmatic': ['pragmatic_plugin/**']},
	ext_modules=[CMakeExtension(name='pragmatic_plugin')],
	cmdclass = {
		'build_ext': cmake_build_ext,
		'install_egg_info': cmake_egg_info
	},
	install_requires = [
		'click',
	],
)