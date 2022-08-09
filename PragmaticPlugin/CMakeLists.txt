cmake_minimum_required(VERSION 3.24)

project(PragmaticPlugin LANGUAGES CXX)

# Output
set(PROJECT "${PROJECT_SOURCE_DIR}/Build/")
set(LIBRARY_OUTPUT_PATH "${PROJECT_SOURCE_DIR}/Build/")

# LLVM
include_directories("${PROJECT_SOURCE_DIR}/../Install/include" "${PROJECT_SOURCE_DIR}/../External/json/single_include")
link_directories("${PROJECT_SOURCE_DIR}/../Install/lib/")

# Project type
add_library(PragmaticPlugin SHARED "Source/Pragmatic.cpp" "Source/SourcePragmaHandler.cpp" "Source/Globals.cpp" "Source/BuildTypePragmaHandler.cpp" "Source/StandardPragmaHandler.cpp" "Source/DirectoryPragmaHandler.cpp" "Source/PythonPragmaHandler.cpp" "Source/PreamblePragmaHandler.cpp")

# Properties
set_property(TARGET PragmaticPlugin PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
set_property(TARGET PragmaticPlugin PROPERTY CXX_STANDARD 14)

# Link
target_link_libraries(PragmaticPlugin clang.lib)