project(BOTs LANGUAGES CXX)

# Output
set(PROJECT "${PROJECT_SOURCE_DIR}/Build/")
set(LIBRARY_OUTPUT_PATH "${PROJECT_SOURCE_DIR}/Build/")

# LLVM
include_directories("${ROOT_DIR}/Tools/LLVM/include" "${ROOT_DIR}/Dependencies/JSON/single_include")
link_directories("${ROOT_DIR}/Tools/LLVM/lib/")

# Project type
add_library(PragmaticPlugin SHARED "Source/Pragmatic.cpp" "Source/SourcePragmaHandler.cpp" "Source/Globals.cpp" "Source/BuildTypePragmaHandler.cpp" "Source/StandardPragmaHandler.cpp" "Source/DirectoryPragmaHandler.cpp" "Source/PythonPragmaHandler.cpp" "Source/PreamblePragmaHandler.cpp")

# Properties
set_property(TARGET PragmaticPlugin PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
set_property(TARGET PragmaticPlugin PROPERTY CXX_STANDARD 14)

# Link
target_link_libraries(PragmaticPlugin clang.lib)