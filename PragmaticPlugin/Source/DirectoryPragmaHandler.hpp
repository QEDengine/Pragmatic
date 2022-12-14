#pragma once

// Standard library
#include <vector>	// vector
#include <string>	// string

// Clang
#include <clang/Lex/Pragma.h>			// PragmaHandler
#include <clang/Lex/Preprocessor.h>		// PragmaHandlerRegistry

namespace QED { namespace Pragmatic
{
	class DirectoryPragmaHandler : public clang::PragmaHandler
	{
	public: // Constructor
		DirectoryPragmaHandler() : clang::PragmaHandler("dir") { }

	public: // Clang functions
		void HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken);

	private:
		void AddBuildTypeToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location);
	};
}} // namespace QED::Pragmatic
