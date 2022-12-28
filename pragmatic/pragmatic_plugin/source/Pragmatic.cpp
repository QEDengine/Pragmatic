


// Clang
#include <clang/Lex/Preprocessor.h>
#include <llvm/Support/Registry.h>
#include <clang/Frontend/FrontendPluginRegistry.h>

// Pragmatic
#include "LanguageOptions.hpp"
#include "Relations.hpp"
#include "Callbacks.hpp"
// #include "Compile.hpp"

static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::PreamblePragmaHandler>		X0("preamblePragma", "Pragma used for running code at the beginning of the file");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::StandardPragma>			X1("standardPragma", "Pragma used to define the C++ language standard");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::ObjectPragma>				X2("objectPragma", "Pragma used to define which .cpp files to build");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::LinkPragma>				X3("linkPragma", "Pragma used to define which object files to link");
// static clang::FrontendPluginRegistry::Add<QED::Pragmatic::RecompileAction>			X4("", "");