


// Clang
#include <clang/Lex/Preprocessor.h>
#include <llvm/Support/Registry.h>

// Pragmatic
#include "SourcePragmaHandler.hpp"
#include "BuildTypePragmaHandler.hpp"
#include "StandardPragmaHandler.hpp"
#include "DirectoryPragmaHandler.hpp"
#include "PythonPragmaHandler.hpp"
#include "PreamblePragmaHandler.hpp"

static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::SourcePragmaHandler>	 X1("sourcePragma",      "Pragma used for source file declaration");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::BuildTypePragmaHandler> X2("buildTypePragma",   "Pragma used for configuring build type");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::StandardPragmaHandler>  X3("standardPragma",    "Pragma used for configuring C++ standard");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::DirectoryPragmaHandler> X4("directoryPragma",   "Pragma used for configuring build directories");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::PythonPragmaHandler>    X5("pythonPragma",   	 "Pragma used for running python macros");
static clang::PragmaHandlerRegistry::Add<QED::Pragmatic::PreamblePragmaHandler>  X6("preamblePragma",    "Pragma used for running code at the beginning of the file");







// #include <clang/Frontend/FrontendAction.h>
// template class llvm::Registry<clang::PreprocessorFrontendAction>;
// using PreprocessorRegistry = llvm::Registry<clang::PreprocessorFrontendAction>;
// LLVM_INSTANTIATE_REGISTRY(PreprocessorRegistry);
// static PreprocessorRegistry::Add<QED::Pragmatic::TestPreprocessorFrontendAction> Y("callbacks", "asdf");