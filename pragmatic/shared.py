from pathlib import Path
from typing import Final
import json

# Constants
PRAGMATIC_MACRO: Final[str] = 'PRAGMATIC_FILE_PATH'
META_FILE: Final[str] = 'meta.json'

# Paths
pragmatic_path: Path = Path(__file__).parent.resolve()
clang_path = f'{pragmatic_path}/LLVM/bin/clang.exe'
pragmatic_plugin_path = f'{pragmatic_path}/pragmatic_plugin/build/PragmaticPlugin.dll'
initial_path: Path = None
initial_path_dir: Path = None
meta_path: Path = None
pragmatic_include_path: Path = pragmatic_path.joinpath('include')
pragmatic_preamble_path: Path = pragmatic_include_path.joinpath('preamble.hpp')

# Variables
meta: json = None
server: bool = False
iteration_count: int = 0