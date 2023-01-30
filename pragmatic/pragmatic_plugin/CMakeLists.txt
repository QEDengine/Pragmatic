cmake_minimum_required(VERSION 3.20)

project(PragmaticPlugin LANGUAGES CXX)

# Output
set(PROJECT "${PROJECT_SOURCE_DIR}/build/")
set(LIBRARY_OUTPUT_PATH "${PROJECT_SOURCE_DIR}/build/")

# LLVM
include_directories("${PROJECT_SOURCE_DIR}/../LLVM/include" "${PROJECT_SOURCE_DIR}/../../external/json/single_include")
link_directories("${PROJECT_SOURCE_DIR}/../LLVM/lib/")

# Sources
file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS source/*.cpp source/*.h)

# Project type
add_library(PragmaticPlugin SHARED ${SOURCES})

# Properties
set_property(TARGET PragmaticPlugin PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
set_property(TARGET PragmaticPlugin PROPERTY CXX_STANDARD 17)

# Link
target_link_libraries(PragmaticPlugin clang.lib)