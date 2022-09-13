from pathlib import Path
from typing import Final

# Constants
PRAGMATIC_MACRO: Final[str] = 'PRAGMATIC_FILE_PATH'
META_FILE: Final[str] = 'meta.json'

# Paths
pragmatic_path: Path = Path(__file__).parent.resolve()
clang_path = f'{pragmatic_path}/LLVM/bin/clang.exe'
pragmatic_plugin_path = f'{pragmatic_path}/pragmatic_plugin/build/PragmaticPlugin.dll'
initial_path: Path = None
meta_path: Path = None