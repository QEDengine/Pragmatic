


// Clang
#include <clang/Lex/Preprocessor.h>
#include <llvm/Support/Registry.h>
#include <clang/Frontend/FrontendPluginRegistry.h>

// Pragmatic
#include "SourcePragmaHandler.hpp"
#include "BuildTypePragmaHandler.hpp"
#include "StandardPragmaHandler.hpp"
#include "DirectoryPragmaHandler.hpp"
#include "PythonPragmaHandler.hpp"
#include "PreamblePragmaHandler.hpp"
#include "TargetPragmaHandler.hpp"
#include "IncludeHandler.hpp"

static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::SourcePragmaHandler>	 X0("sourcePragma",      "Pragma used for source file declaration");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::BuildTypePragmaHandler> X1("buildTypePragma",   "Pragma used for configuring build type");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::StandardPragmaHandler>  X2("standardPragma",    "Pragma used for configuring C++ standard");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::DirectoryPragmaHandler> X3("directoryPragma",   "Pragma used for configuring build directories");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::PythonPragmaHandler>    X4("pythonPragma",   	 "Pragma used for running python macros");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::PreamblePragmaHandler>  X5("preamblePragma",    "Pragma used for running code at the beginning of the file");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::TargetPragmaHandler>	 X6("targetPragma",		 "Pragma used for defining build targets");



// #include <clang/Frontend/FrontendAction.h>
// template class llvm::Registry<clang::PreprocessorFrontendAction>;
// using PreprocessorRegistry = llvm::Registry<clang::PreprocessorFrontendAction>;
// LLVM_INSTANTIATE_REGISTRY(PreprocessorRegistry);
// static PreprocessorRegistry::Add<QED::Pragmatic::TestPreprocessorFrontendAction> Y("callbacks", "asdf");